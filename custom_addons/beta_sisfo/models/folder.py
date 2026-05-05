from odoo import api, fields, models


class BetaFolder(models.Model):
    _name = "beta.folder"
    _description = "BETA Project Folder"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, name"

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True, tracking=True)
    code = fields.Char(required=True, tracking=True)
    description = fields.Text()
    workspace_id = fields.Many2one("beta.workspace", required=True, tracking=True)
    owner_id = fields.Many2one("res.users", default=lambda self: self.env.user, tracking=True)
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
    document_ids = fields.One2many("beta.controlled.document", "folder_id", string="Documents")
    document_count = fields.Integer(compute="_compute_counts")
    validated_document_count = fields.Integer(compute="_compute_counts")

    _sql_constraints = [
        ("beta_folder_code_uniq", "unique(code)", "Folder code must be unique."),
    ]

    @api.depends("document_ids.state")
    def _compute_counts(self):
        for folder in self:
            folder.document_count = len(folder.document_ids)
            folder.validated_document_count = len(folder.document_ids.filtered(lambda doc: doc.state == "validated"))
