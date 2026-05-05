from odoo import api, fields, models


class BetaWorkspace(models.Model):
    _name = "beta.workspace"
    _description = "BETA Workspace"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(required=True, tracking=True)
    description = fields.Text()
    owner_id = fields.Many2one("res.users", string="Owner", default=lambda self: self.env.user, tracking=True)
    member_ids = fields.Many2many("res.users", string="Members")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("ongoing", "On Going"),
            ("done", "Done"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    active = fields.Boolean(default=True)
    folder_ids = fields.One2many("beta.folder", "workspace_id", string="Folders")
    requirement_ids = fields.One2many("beta.requirement", "workspace_id", string="Requirements")
    document_ids = fields.One2many("beta.controlled.document", "workspace_id", string="Documents")
    folder_count = fields.Integer(compute="_compute_counts")
    requirement_count = fields.Integer(compute="_compute_counts")
    validated_requirement_count = fields.Integer(compute="_compute_counts")
    document_count = fields.Integer(compute="_compute_counts")
    validated_document_count = fields.Integer(compute="_compute_counts")
    pending_document_count = fields.Integer(compute="_compute_counts")

    _sql_constraints = [
        ("beta_workspace_code_uniq", "unique(code)", "Workspace code must be unique."),
    ]

    @api.depends("requirement_ids.state", "document_ids.state")
    def _compute_counts(self):
        for workspace in self:
            workspace.folder_count = len(workspace.folder_ids)
            workspace.requirement_count = len(workspace.requirement_ids)
            workspace.validated_requirement_count = len(
                workspace.requirement_ids.filtered(lambda req: req.state == "validated")
            )
            workspace.document_count = len(workspace.document_ids)
            workspace.validated_document_count = len(
                workspace.document_ids.filtered(lambda doc: doc.state == "validated")
            )
            workspace.pending_document_count = len(
                workspace.document_ids.filtered(lambda doc: doc.state in ("draft", "submitted", "revision"))
            )
