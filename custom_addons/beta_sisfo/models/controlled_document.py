import re

from odoo import api, fields, models


class BetaControlledDocument(models.Model):
    _name = "beta.controlled.document"
    _description = "BETA Controlled Document"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "write_date desc, id desc"

    name = fields.Char(required=True, tracking=True)
    reference = fields.Char(default="New", copy=False, readonly=True, index=True)
    requirement_id = fields.Many2one("beta.requirement", required=True, tracking=True)
    folder_id = fields.Many2one("beta.folder", tracking=True)
    workspace_id = fields.Many2one("beta.workspace", related="requirement_id.workspace_id", store=True, readonly=True)
    project_id = fields.Many2one("project.project", related="requirement_id.project_id", store=True, readonly=True)
    owner_id = fields.Many2one("res.users", string="Uploaded By", default=lambda self: self.env.user, readonly=True)
    category = fields.Selection(
        [
            ("specification", "Specification"),
            ("contract", "Contract"),
            ("sop", "SOP"),
            ("other", "Other"),
        ],
        default="specification",
        required=True,
        tracking=True,
    )
    version = fields.Char(default="v1", tracking=True)
    file = fields.Binary(attachment=True)
    file_name = fields.Char()
    notes = fields.Text()
    previous_document_id = fields.Many2one("beta.controlled.document", string="Previous Version", readonly=True, copy=False)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("revision", "Needs Revision"),
            ("rejected", "Rejected"),
            ("validated", "Validated"),
            ("obsolete", "Obsolete"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    validated_by_id = fields.Many2one("res.users", readonly=True)
    validated_on = fields.Datetime(readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("reference", "New") == "New":
                vals["reference"] = self.env["ir.sequence"].next_by_code("beta.controlled.document") or "DOC-0000"
        records = super().create(vals_list)
        for record in records:
            self.env["beta.audit.log"].log_action(
                record,
                "Document created",
                "Controlled document draft created.",
                action_type="create",
            )
        return records

    def action_submit(self):
        for record in self:
            record.write({"state": "submitted"})
            record.message_post(body="Document submitted for review.")
            self.env["beta.audit.log"].log_action(
                record,
                "Document submitted",
                "Submitted for validation.",
                action_type="submit",
            )
        return True

    def action_request_revision(self):
        for record in self:
            record.write({"state": "revision"})
            record.message_post(body="Document returned for revision.")
            self.env["beta.audit.log"].log_action(
                record,
                "Document revision requested",
                record.notes or "",
                action_type="revision",
            )
        return True

    def action_reject(self):
        for record in self:
            record.write({"state": "rejected"})
            record.message_post(body="Document rejected.")
            self.env["beta.audit.log"].log_action(
                record,
                "Document rejected",
                record.notes or "",
                action_type="reject",
            )
        return True

    def action_validate(self):
        for record in self:
            record.write(
                {
                    "state": "validated",
                    "validated_by_id": self.env.user.id,
                    "validated_on": fields.Datetime.now(),
                }
            )
            record.message_post(body="Document validated.")
            self.env["beta.audit.log"].log_action(
                record,
                "Document validated",
                f"Validated version {record.version}.",
                action_type="validate",
            )
        return True

    def action_reset_draft(self):
        for record in self:
            record.write({"state": "draft"})
            record.message_post(body="Document reset to draft.")
            self.env["beta.audit.log"].log_action(
                record,
                "Document reset",
                "Returned to draft state.",
                action_type="reset",
            )
        return True

    def action_create_revision(self):
        self.ensure_one()
        next_version = self._next_version(self.version)
        new_doc = self.copy(
            {
                "name": f"{self.name} Revision",
                "version": next_version,
                "state": "draft",
                "validated_by_id": False,
                "validated_on": False,
                "previous_document_id": self.id,
            }
        )
        self.write({"state": "obsolete"})
        self.message_post(body=f"Revision {next_version} created as {new_doc.display_name}.")
        self.env["beta.audit.log"].log_action(
            self,
            "Document obsoleted",
            f"Replaced by revision {next_version} ({new_doc.reference}).",
            action_type="revision",
        )
        self.env["beta.audit.log"].log_action(
            new_doc,
            "Revision created",
            f"Created from {self.reference} with version {next_version}.",
            action_type="revision",
        )
        return {
            "type": "ir.actions.act_window",
            "name": "Revision Document",
            "res_model": "beta.controlled.document",
            "view_mode": "form",
            "res_id": new_doc.id,
            "target": "current",
        }

    @staticmethod
    def _next_version(current_version):
        match = re.search(r"(\d+)$", current_version or "")
        if not match:
            return "v2"
        return f"v{int(match.group(1)) + 1}"
