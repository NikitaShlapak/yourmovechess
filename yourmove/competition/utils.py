import berserk


class BetterTeam(berserk.clients.BaseClient):
    def join(self, team_id, password=None, message=None):
        """Join a team.

        :param str team_id: ID of a team
        :return: success
        :rtype: bool
        """
        data = {}
        if password:
            data['password'] = password
        if message:
            data['message'] = message
        path = f'/team/{team_id}/join'
        return self._r.post(path, data=data)


class BetterSwiss(berserk.clients.BaseClient):
    def join(self, swiss_id, password=None):
        data = {}
        if password:
            data['password'] = password
        path = f'api/swiss/{swiss_id}/join'
        print(path)
        return self._r.post(path, data=data)


class DataMixin:
    def get_user_context(self, **kwargs):
        context = kwargs
        return context

def format_string(string):
    return string.lower().replace('ё','е')