from odoo import _, fields, models


class BetaUserProfile(models.TransientModel):
    _name = "beta.user.profile"
    _description = "BETA User Profile"

    user_id = fields.Many2one("res.users", required=True, readonly=True)
    name = fields.Char(readonly=True)
    login = fields.Char(readonly=True)
    email = fields.Char(readonly=True)
    role_label = fields.Char(readonly=True)

    @staticmethod
    def _get_role_label(user):
        if user.has_group("beta_sisfo.group_beta_coo"):
            return "Chief Operating Officer"
        if user.has_group("beta_sisfo.group_beta_project_officer"):
            return "Project Officer"
        if user.has_group("beta_sisfo.group_beta_engineering"):
            return "Engineering"
        if user.has_group("beta_sisfo.group_beta_sales"):
            return "Sales"
        return "Internal User"

    def _current_profile_values(self):
        user = self.env.user.sudo()
        return {
            "user_id": self.env.user.id,
            "name": user.name,
            "login": user.login,
            "email": user.email,
            "role_label": self._get_role_label(self.env.user),
        }

    def action_open_my_profile(self):
        profile = self.create(self._current_profile_values())
        return {
            "type": "ir.actions.act_window",
            "name": _("My Profile"),
            "res_model": "beta.user.profile",
            "view_mode": "form",
            "view_id": self.env.ref("beta_sisfo.view_beta_user_profile_form").id,
            "res_id": profile.id,
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
            "context": {"default_user_id": self.env.user.id},
        }
