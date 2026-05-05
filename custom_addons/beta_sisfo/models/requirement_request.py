from odoo import api, fields, models


class BetaRequirement(models.Model):
    _name = "beta.requirement"
    _description = "BETA Requirement Validation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "write_date desc, id desc"

    name = fields.Char(required=True, tracking=True)
    reference = fields.Char(default="New", copy=False, readonly=True, index=True)
    workspace_id = fields.Many2one("beta.workspace", required=True, tracking=True)
    requested_by_id = fields.Many2one(
        "res.users", string="Requested By", default=lambda self: self.env.user, readonly=True
    )
    engineer_id = fields.Many2one("res.users", string="Engineering Owner", tracking=True)
    project_officer_id = fields.Many2one("res.users", string="Project Officer", tracking=True)
    client_name = fields.Char(required=True, tracking=True)
    requirement_summary = fields.Text(required=True)
    file = fields.Binary(attachment=True)
    file_name = fields.Char()
    attachment_ids = fields.Many2many(
        "ir.attachment",
        "beta_requirement_attachment_rel",
        "requirement_id",
        "attachment_id",
        string="Additional Attachments",
    )
    sales_notes = fields.Text()
    engineering_notes = fields.Text()
    revision_feedback = fields.Text()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("revision", "Needs Revision"),
            ("validated", "Validated"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    lead_id = fields.Many2one("crm.lead", string="CRM Opportunity", readonly=True, copy=False)
    project_id = fields.Many2one("project.project", string="Project", readonly=True, copy=False)
    validated_by_id = fields.Many2one("res.users", readonly=True)
    validated_on = fields.Datetime(readonly=True)
    document_ids = fields.One2many("beta.controlled.document", "requirement_id", string="Controlled Documents")
    document_count = fields.Integer(compute="_compute_document_metrics")
    validated_document_count = fields.Integer(compute="_compute_document_metrics")
    readiness_percent = fields.Integer(compute="_compute_document_metrics")

    def _compute_document_metrics(self):
        for req in self:
            total = len(req.document_ids)
            validated = len(req.document_ids.filtered(lambda doc: doc.state == "validated"))
            req.document_count = total
            req.validated_document_count = validated
            req.readiness_percent = int((validated / total) * 100) if total else (100 if req.state == "validated" else 0)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("reference", "New") == "New":
                vals["reference"] = self.env["ir.sequence"].next_by_code("beta.requirement") or "REQ-0000"
        records = super().create(vals_list)
        for record in records:
            self.env["beta.audit.log"].log_action(
                record,
                "Requirement created",
                "Initial draft created.",
                action_type="create",
            )
        return records

    def action_submit(self):
        for record in self:
            record.write({"state": "submitted"})
            record.message_post(body="Requirement submitted for validation.")
            self.env["beta.audit.log"].log_action(
                record,
                "Requirement submitted",
                "Submitted by business owner.",
                action_type="submit",
            )
        return True

    def action_request_revision(self):
        for record in self:
            record.write({"state": "revision"})
            record.message_post(body="Requirement returned for revision.")
            self.env["beta.audit.log"].log_action(
                record,
                "Revision requested",
                record.revision_feedback or "",
                action_type="revision",
            )
        return True

    def action_reject(self):
        for record in self:
            record.write({"state": "rejected"})
            record.message_post(body="Requirement rejected.")
            self.env["beta.audit.log"].log_action(
                record,
                "Requirement rejected",
                record.revision_feedback or "",
                action_type="reject",
            )
        return True

    def action_reset_draft(self):
        for record in self:
            record.write({"state": "draft"})
            record.message_post(body="Requirement reset to draft.")
            self.env["beta.audit.log"].log_action(
                record,
                "Requirement reset",
                "Record returned to draft.",
                action_type="reset",
            )
        return True

    def action_validate(self):
        for record in self:
            if not record.lead_id:
                lead = self.env["crm.lead"].sudo().create(
                    {
                        "name": record.name,
                        "partner_name": record.client_name,
                        "description": record.requirement_summary,
                        "type": "opportunity",
                    }
                )
                record.lead_id = lead.id
            if not record.project_id:
                project = self.env["project.project"].sudo().create(
                    {
                        "name": record.name,
                    }
                )
                record.project_id = project.id
            record.write(
                {
                    "state": "validated",
                    "validated_by_id": self.env.user.id,
                    "validated_on": fields.Datetime.now(),
                }
            )
            record.message_post(body="Requirement validated and linked to CRM/Project.")
            self.env["beta.audit.log"].log_action(
                record,
                "Requirement validated",
                f"Linked CRM lead: {record.lead_id.display_name or '-'} | Project: {record.project_id.display_name or '-'}",
                action_type="validate",
            )
        return True
