from odoo import _, api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    beta_role_label = fields.Char(compute="_compute_beta_role_label")

    @api.depends("groups_id")
    def _compute_beta_role_label(self):
        for user in self:
            if user.has_group("beta_sisfo.group_beta_coo"):
                user.beta_role_label = "Chief Operating Officer"
            elif user.has_group("beta_sisfo.group_beta_project_officer"):
                user.beta_role_label = "Project Officer"
            elif user.has_group("beta_sisfo.group_beta_engineering"):
                user.beta_role_label = "Engineering"
            elif user.has_group("beta_sisfo.group_beta_sales"):
                user.beta_role_label = "Sales"
            else:
                user.beta_role_label = "Internal User"

    @api.model
    def action_open_my_profile(self):
        return {
            "type": "ir.actions.act_window",
            "name": _("My Profile"),
            "res_model": "res.users",
            "view_mode": "form",
            "view_id": self.env.ref("beta_sisfo.view_beta_user_profile_form").id,
            "res_id": self.env.user.id,
            "target": "current",
        }

    def action_open_password_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Change Password"),
            "res_model": "beta.change.password.wizard",
            "view_mode": "form",
            "view_id": self.env.ref("beta_sisfo.view_beta_change_password_wizard_form").id,
            "target": "new",
            "context": {"default_user_id": self.id},
        }
