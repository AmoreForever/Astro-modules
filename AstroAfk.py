__version__ = (2, 0, 0)
#                _             __  __           _       _                
#      /\       | |           |  \/  |         | |     | |               
#     /  \   ___| |_ _ __ ___ | \  / | ___   __| |_   _| | ___  ___      
#    / /\ \ / __| __| '__/ _ \| |\/| |/ _ \ / _` | | | | |/ _ \/ __|     
#   / ____ \\__ \ |_| | | (_) | |  | | (_) | (_| | |_| | |  __/\__ \     
#  /_/    \_\___/\__|_|  \___/|_|  |_|\___/ \__,_|\__,_|_|\___||___/     
#                                                                        
#                         © Copyright 2023                             
#                                                                        
#                https://t.me/Den4ikSuperOstryyPer4ik                    
#                              and                                       
#                      https://t.me/ToXicUse                             
#                                                                         
#                 🔒 Licensed under the GNU AGPLv3                       
#             https://www.gnu.org/licenses/agpl-3.0.html                 
#                   
# meta banner: https://0x0.st/oFwG.jpg                                                                                            
# meta developer: @AstroModules
# meta designer: @XizurK

import time
import logging
import datetime
from telethon import types
from .. import loader, utils
from ..inline.types import InlineCall
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.account import UpdateProfileRequest

logger = logging.getLogger(__name__)


class AstroAfkMod(loader.Module):
	"""Полностью настраиваемый модуль для ухода в АФК режим! Обновление TxAFK!"""

	async def client_ready(self, client, db):
		self._db = db
		self._me = await client.get_me()

	strings = {
		"name": "AstroAFK",

		"lname": "| afk.",
		"lname0": " ",

		"bt_off_afk": "⚠️ АФК режим отключен",
		"bt_on_afk": "💤 АФК режим снова активен",

		"_cfg_cst_btn": "Ссылка на чат, которая будет находиться под текстом АФК. Чтобы вовсе убрать, напишите None",
		"feedback_bot__text": "Юзернейм вашего feedback бота. Если нету - не трогайте",
		"button__text": "Добавить инлайн кнопку отключения АФК режима?",
		"custom_text__afk_text": "Кастомный текст афк. Используй {time} для вывода последнего времени нахождения в сети",
	}

	def render_settings(self):
		active = self._db.get(__name__, 'afk')
		if active == True:
			a_active = "Включен ✅"
		else:
			a_active = 'Выключен 🚫'
		change_bio = self._db.get(__name__, 'change_bio')
		if change_bio == True:
			a_change_bio = 'Да'
		else:
			a_change_bio = 'Нет'
		change_name = self._db.get(__name__, 'change_name')
		if change_name == True:
			a_change_name = 'Да'
		else:
			a_change_name = 'Нет'
		fb = self.config['feedback_bot']
		text = (
			f'🥷🏼 <b>TxAFK</b>\n'
			f'├<b>{a_active}</b>\n'
			f'<b>├Смена биографии:</b> <code>{a_change_bio}</code> 📖\n'
			f'<b>├Смена префикса:</b> <code>{a_change_name}</code> 📝\n'
			f'<b>└Бот для связи:</b> <code>@{fb}</code> 🤖'
		)
		return text


	def __init__(self):
		self.config = loader.ModuleConfig(
			loader.ConfigValue(
				"prefix",
				'| afk.',
				doc=lambda: 'Префикс, который будет добавляться к вашему имени во время входа в АФК'
			),
			loader.ConfigValue(
				"feedback_bot",
				None,
				doc=lambda: self.strings("feedback_bot__text"),
			),
			loader.ConfigValue(
				"custom_text__afk",
				"None",
				doc=lambda: self.strings("custom_text__afk_text"),
			),
			loader.ConfigValue(
				"custom_button",
				[
					"🦄 AstroModules 🦄",
					"https://t.me/AstroModulesChat",
				],
				lambda: self.strings("_cfg_cst_btn"),
				validator=loader.validators.Union(
					loader.validators.Series(fixed_len=2),
					loader.validators.NoneType(),
				),
			),
			loader.ConfigValue(
				"ignore_chats",
				[],
				lambda: "Чаты, в которых TxAFК не будет срабатывать",
				validator=loader.validators.Series(
                    validator=loader.validators.Union(
                        loader.validators.TelegramID(),
                        loader.validators.RegExp("[0-9]"),
                    ),
                ),
			),
			loader.ConfigValue(
				"button",
				True,
				doc=lambda: self.strings("button__text"),
				validator=loader.validators.Boolean(),
			)

		)

	def _afk_custom_text(self) -> str:
		now = datetime.datetime.now().replace(microsecond=0)
		gone = datetime.datetime.fromtimestamp(
			self._db.get(__name__, "gone")
		).replace(microsecond=0)

		time = now - gone

		return (
			"<b> </b>\n"
			+ self.config["custom_text__afk"].format(
				time=time,
			)
		)

	@loader.command()
	async def asst(self, message):
		"""- открыть настройки модуля"""
		
		await self.inline.form(message=message, text='<b>⚙️ Открыть настройки</b>', reply_markup=[{'text': '🔴 Открыть', 'callback': self.settings}])

	@loader.command()
	async def goafk(self, message):
		"""- войти в АФК режим"""
		try:
			user_id = (
				(
					(
						await self._client.get_entity(
							args if not args.isdigit() else int(args)
						)
					).id
				)
				if args
				else reply.sender_id
			)
		except Exception:
			user_id = self._tg_id
		user = await self._client(GetFullUserRequest(user_id))
		
		self._db.set(__name__, "afk", True)
		self._db.set(__name__, "gone", time.time())
		self._db.set(__name__, "ratelimit", [])
		change_bio = self._db.get(__name__, "change_bio")
		change_name = self._db.get(__name__, "change_name")

		try:
			ls = user.full_user.last_name
		except:
			ls = ''
		about = user.full_user.about

		self._db.set(__name__, 'about', about)
		self._db.set(__name__, "ln", ls)

		if change_name == False and change_bio == False:
			await utils.answer(message, '<emoji document_id=5188391205909569136>✅</emoji> <b>АФК</b> режим был успешно <b>включен</b>!')
			return

		if change_name == True:
			prefix = self.config['prefix']
			last_name = f'{ls} {prefix}'
			await message.client(UpdateProfileRequest(last_name=last_name))

		if change_bio == True:
			if self.config['feedback_bot'] == None:
				await message.client(UpdateProfileRequest(about='Нахожусь в афк.', last_name=self.config['prefix']))
			else:
				a_afk_bio = 'Нет на месте, нахожусь в афк. Связь только через: '
				feedback = self.config['feedback_bot']
				await message.client(UpdateProfileRequest(about=f'{a_afk_bio} {feedback}'))

		await utils.answer(message, '<emoji document_id=5188391205909569136>✅</emoji> <b>АФК</b> режим был успешно <b>включен</b>!')
		

	@loader.command()
	async def ungoafk(self, message):
		"""- выйти из режима АФК"""

		self._db.set(__name__, "afk", False)
		self._db.set(__name__, "gone", None)
		self._db.set(__name__, "ratelimit", [])
		change_bio = self._db.get(__name__, "change_bio")
		change_name = self._db.get(__name__, "change_name")

		if change_name == False and change_bio == False:
			await utils.answer(message, '<emoji document_id=5465665476971471368>❌</emoji> <b>АФК</b> режим был успешно <b>выключен</b>!')
			return

		if change_name == True:
			ls = self._db.get(__name__, 'ln')
			await message.client(UpdateProfileRequest(last_name=ls))

		if change_bio == True:
			try:
				await message.client(UpdateProfileRequest(about=f'{self.db.get(__name__, "about")}'))
			except:
				await message.client(UpdateProfileRequest(about="@AstroOfftop - лучший чат для общения."))
		await utils.answer(message, '<emoji document_id=5465665476971471368>❌</emoji> <b>АФК</b> режим был успешно <b>выключен</b>!')
		await self.allmodules.log("TxAFK now stoped.")


	@loader.watcher()
	async def watcher(self, message):
		if not isinstance(message, types.Message):
			return
		if utils.get_chat_id(message) in self.config['ignore_chats']: 
			return
		if message.mentioned or getattr(message.to_id, "user_id", None) == self._me.id:
			afk_state = self.get_afk()
			if not afk_state:
				return
			logger.debug("tagged!")
			ratelimit = self._db.get(__name__, "ratelimit", [])
			if utils.get_chat_id(message) in ratelimit:
				return
			else:
				self._db.setdefault(__name__, {}).setdefault("ratelimit", []).append(
					utils.get_chat_id(message)
				)
				self._db.save()
			user = await utils.get_user(message)
			if user.is_self or user.bot or user.verified:
				logger.debug("User is self, bot or verified.")
				return
			if self.get_afk() is False:
				return
			now = datetime.datetime.now().replace(microsecond=0)
			gone = datetime.datetime.fromtimestamp(
				self._db.get(__name__, "gone")
			).replace(microsecond=0)
			time = now - gone
			if self.config['custom_button'] == None:
				if self.config["button"] == False:
					if self.config["custom_text__afk"] == None:
						await self.inline.form(message=message, text=f"<b>🔅 Я сейчас нахожусь в АФК.</b>\n\nПоследний раз был в сети <code>{time}</code> назад.")
					else:
						await self.inline.form(message=message, text=self._afk_custom_text())
				
				elif self.config['button'] == True:
					if self.config["custom_text__afk"] == None:
						await self.inline.form(
							message=message, 
							text=f"<b>🔅 Я сейчас нахожусь в АФК.</b>\n\nПоследний раз был в сети <code>{time}</code> назад.", 
							reply_markup=[
								[
									{
										"text": "🚫 Выйти с афк 🚫", 
										"callback": self.button_cancel,
									}
								]
							]
						)

					else:
						await self.inline.form(
							message=message, 
							text=self._afk_custom_text(), 
							reply_markup=[
								[
									{
										"text": "🚫 Выйти с афк 🚫", 
										"callback": self.button_cancel,
									}
								]
							]
						)
			else:
				if self.config["button"] == False:
					if self.config["custom_text__afk"] == None:
						await self.inline.form(message=message, text=f"<b>🔅 Я сейчас нахожусь в АФК.</b>\n\nПоследний раз был в сети <code>{time}</code> назад.", reply_markup=[{"text": self.config['custom_button'][0], "url": self.config['custom_button'][1]}])
					else:
						await self.inline.form(message=message, text=self._afk_custom_text(), reply_markup=[{"text": self.config['custom_button'][0], "url": self.config['custom_button'][1]}])
				
				elif self.config['button'] == True:
					if self.config["custom_text__afk"] == None:
						await self.inline.form(
							message=message, 
							text=f"<b>🔅 Я сейчас нахожусь в АФК.</b>\n\nПоследний раз был в сети <code>{time}</code> назад.", 
							reply_markup=[
								[
									{
										"text": self.config['custom_button'][0],
										"url": self.config['custom_button'][1],
									}
								],
								[
									{
										"text": "🚫 Выйти с афк 🚫", 
										"callback": self.button_cancel,
									}
								]
							]
						)

					else:
						await self.inline.form(
							message=message, 
							text=self._afk_custom_text(), 
							reply_markup=[
								[
									{
										"text": self.config['custom_button'][0],
										"url": self.config['custom_button'][1],
									}
								],
								[
									{
										"text": "🚫 Выйти с афк 🚫", 
										"callback": self.button_cancel,
									}
								]
							]
						)

	async def button_cancel(self, call: InlineCall):
		self._db.set(__name__, "afk", False)
		self._db.set(__name__, "gone", None)
		self._db.set(__name__, "ratelimit", [])
		change_bio = self._db.get(__name__, "change_bio")
		change_name = self._db.get(__name__, "change_name")
		self._db.set(__name__, 'about', about)
		self._db.set(__name__, "ln", ls)
		await self.allmodules.log("TxAFК now not working.")

		if change_name == False and change_bio == False:
			await call.edit(self.strings["bt_off_afk"])
			return

		if change_name == True:
			ls = self._db.get(__name__, 'ln')
			await message.client(UpdateProfileRequest(last_name=ls))

		if change_bio == True:
			try:
				await self._client(UpdateProfileRequest(about=f'{self.db.get(__name__, "about")}'))
			except:
				await self._.client(UpdateProfileRequest(about="@AstroOfftop - лучший чат для общения."))

		await call.edit(self.strings["bt_off_afk"])

	async def settings(self, call: InlineCall):
		info = self.render_settings()
		await call.edit(
			text=info,
			reply_markup=[
				[
					{
						'text': "📖 Биография",
						'callback': self.settings_about
					},
					{
						'text': '📝 Префикс',
						'callback': self.settings_name
					}
				],
				[
					{
						"text": "🚫 Закрыть",
						"action": 'close'
					}
				]
			]
		)

	async def settings_name(self, call: InlineCall):
		await call.edit(
			text=(
				f'<b>📖 Установка префикса</b>\n\n'
				+ '<i>❔ Хотите ли Вы, чтобы при входе в АФК режим к вашему '
				+ 'нику добавлялся префикс <code>| afk.</code> ?</i>\n\n'
				+ 'ℹ️ Так же Вы можете <b>изменить префикс</b>, '
				+ '<b>отменить</b> или <b>сделать</b> действие, нажав на <b>кнопки ниже</b>'
			),
			reply_markup=[
				[
					{
						'text': '✅ Да',
						"callback": self.name_yes
					},
					{
						"text": '🚫 Нет',
						"callback": self.name_no
					}
				],
				[{'text': '↩️ Назад', 'callback': self.settings}]
			]
		)
	async def name_yes(self, call: InlineCall):
		self._db.set(__name__, 'change_name', True)
		info = self.render_settings()
		await call.edit(
			text=info,
			reply_markup=[
				[
					{
						'text': "📖 Биография",
						'callback': self.settings_about
					},
					{
						'text': '📝 Префикс',
						'callback': self.settings_name
					}
				],
				[
					{
						"text": "🚫 Закрыть",
						"action": 'close'
					}
				]
			]
		)
	async def name_no(self, call: InlineCall):
		self._db.set(__name__, 'change_name', False)
		info = self.render_settings()
		await call.edit(
			text=info,
			reply_markup=[
				[
					{
						'text': "📖 Биография",
						'callback': self.settings_about
					},
					{
						'text': '📝 Префикс',
						'callback': self.settings_name
					}
				],
				[
					{
						"text": "🚫 Закрыть",
						"action": 'close'
					}
				]
			]
		)
	async def settings_about(self, call: InlineCall):
		if self.config['feedback_bot'] == None:
			text = (
				f'📖 <b>Смена биографии</b>'
				+ '\n\n❔ <b>Хотите</b> ли Вы, чтобы при <b>входе в АФК</b> режим Ваша биография <b>менялась</b>'
				+ '  на "<code>Нахожусь в афк</code>"?\n\n'
				+ 'ℹ️ Так же Вы можете <b>изменить биографию</b> в <b>конфиге</b>. '
				+ 'Можно <b>отменить</b> или <b>сделать</b> действие, нажав на <b>кнопки ниже</b>'
			)
		else:
			text = (
				f'📖 <b>Смена биографии</b>'
				+ '\n\n❔ <b>Хотите</b> ли Вы, чтобы при <b>входе в АФК</b> режим '
				+ 'Ваша биография <b>менялась</b> на  "<code>Нет, на месте нахожусь в афк</code><code>.'
				+ f' Связь только через @{self.config["feedback_bot"]}</code>"?\n🤖 <b>Бот для связи</b>: <code>@{self.config["feedback_bot"]}</code>\n\n'
				+ 'ℹ️ Так же Вы можете <b>изменить биографию</b> в <b>конфиге</b>. '
				+ 'Можно <b>отменить</b> или <b>сделать</b> действие, нажав на <b>кнопки ниже</b>'
			)
		await call.edit(
			text=text,
			reply_markup=[
				[
					{
						'text': '✅ Да',
						"callback": self.bio
					},
					{
						"text": '🚫 Нет',
						"callback": self.bio_n
					}
				],
				[{'text': '↩️ Назад', 'callback': self.settings}]
			]
		)
	async def bio(self, call: InlineCall):
		self._db.set(__name__, 'change_bio', True)
		info = self.render_settings()
		await call.edit(
			text=info,
			reply_markup=[
				[
					{
						'text': "📖 Биография",
						'callback': self.settings_about
					},
					{
						'text': '📝 Префикс',
						'callback': self.settings_name
					}
				],
				[
					{
						"text": "🚫 Закрыть",
						"action": 'close'
					}
				]
			]
		)
	async def bio_n(self, call: InlineCall):
		self._db.set(__name__, 'change_bio', False)
		info = self.render_settings()
		await call.edit(
			text=info,
			reply_markup=[
				[
					{
						'text': "📖 Биография",
						'callback': self.settings_about
					},
					{
						'text': '📝 Префикс',
						'callback': self.settings_name
					}
				],
				[
					{
						"text": "🚫 Закрыть",
						"action": 'close'
					}
				]
			]
		)

	def get_afk(self):
		return self._db.get(__name__, "afk", False)