from .. import db
from datetime import datetime
from app.exceptions import ValidationError
from app.utils import filter_upload_url, datetime_timestamp


class Game(db.Model):
    __tablename__ = 'tb_game'
    id = db.Column(db.Integer, primary_key=True)
    game_name = db.Column(db.String(50), index=True)
    icon_url = db.Column(db.String(150))
    banner_url = db.Column(db.String(150))
    music_url = db.Column(db.String(150))
    package_name = db.Column(db.String(250))
    data_file_names = db.Column(db.Text)
    game_desc = db.Column(db.Text)
    gift_desc = db.Column(db.Text)
    gift_url = db.Column(db.String(150))
    qr_url = db.Column(db.String(150))
    apk_url = db.Column(db.String(150))
    add_time = db.Column(db.DateTime(), default=datetime.now)
    state = db.Column(db.Integer, default=1)

    @staticmethod
    def from_json(json_game):
        game = Game()
        game.game_name = json_game.get('game_name')
        if game.game_name is None or game.game_name == '':
            raise ValidationError('game does not have a name')
        return game

    def to_json(self):
        json_game = {
            'id': self.id,
            'game_name': self.game_name,
            'package_name': self.package_name,
            'data_file_names': self.data_file_names,
            'icon_url': filter_upload_url(self.icon_url),
            'banner_url': filter_upload_url(self.banner_url),
            'music_url': filter_upload_url(self.music_url),
            'add_time': datetime_timestamp(self.add_time),
            'game_desc': self.game_desc,
            'gift_desc': self.gift_desc,
            'gift_url': self.gift_url,
            'qr_url': self.qr_url,
            'apk_url': self.apk_url,
            'state': self.state,
        }
        return json_game

    def __repr__(self):
        return '<Game %r>' % self.game_name