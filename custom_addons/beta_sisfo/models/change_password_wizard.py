from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class BetaChangePasswordWizard(models.TransientModel):
    _name = "beta.change.password.wizard"
    _description = "BETA Change Password Wizard"

    user_id = fields.Many2one("res.users", required=True, readonly=True, default=lambda self: self.env.user)
    new_password = fields.Char(required=True)
    confirm_password = fields.Char(required=True)

    @api.constrains("new_password", "confirm_password")
    def _check_password_match(self):
        for wizard in self:
            if wizard.new_password != wizard.confirm_password:
                raise ValidationError(_("Password confirmation does not match."))

    def action_apply(self):
        self.ensure_one()
        self.user_id.sudo().write({"password": self.new_password})
        return {"type": "ir.actions.act_window_close"}
