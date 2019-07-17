import img2pdf
import aiohttp
import asyncio
from io import BytesIO
import PIL.Image as Image
from telethon import TelegramClient

API_ID = 724808#циферки
API_HASH = '4b7dc63672dde8d051caf717af758987'#букофки
PRIVATE = -1001213568715
client = TelegramClient(f'test-session', API_ID, API_HASH)
client.start()

class ImgListPDF:
	def __init__(self, img_list, bot, message):
		self.img_list = img_list
		self.bot = bot
		self.message = message
		#self.loop = asyncio.get_event_loop()
		#self.loop.run_until_complete(self.load(img_list))
		#self.img_list = img_list

	async def load(self, max_width = 1080):
		tmp = []
		number = 0
		for i in self.img_list:
			
			await self.bot.edit_message_text( chat_id =self.message.chat.id, message_id = self.message.message_id, 
					text = '%.2f ' % (number*100/len(self.img_list)  ) + '% pictures loaded...')
			async with aiohttp.ClientSession() as session:
				async with session.get(i) as r:
					if r.status == 200:
						f =  BytesIO()
						while True:
							i = await r.content.read(10**4)
							if not i: break
							f.write(i) 
						i = Image.open(f)
						i.thumbnail((max_width, max_width*5),  Image.ANTIALIAS)
						f =  BytesIO()
						i.convert('RGB').save(f, "JPEG")
						tmp.append( f.getvalue())
					else: print(r)
			number+= 1
		await self.bot.edit_message_text(chat_id = self.message.chat.id, message_id = self.message.message_id, 
					text = '100% pictures loaded!')
		self.img_list = tmp
		
	


	async def pdfbook(self, name):
		await self.load()
		pdf = img2pdf.convert(self.img_list)
		with open(name, 'wb') as f:
			f.write(pdf)

		await client.send_file(PRIVATE, name, caption = 'send_to_user: '+ str(self.message.chat.id))
		await self.bot.delete_message(chat_id = self.message.chat.id, message_id = self.message.message_id)
		





