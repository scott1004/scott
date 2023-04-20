from line_bot_api import *


def about_us_event(event):
    emoji = [
        {
            "index": 0,
            "productId": "5ac2213e040ab15980c9b447",
            "emojiId": "001"
        },
        {
            "index": 7,
            "productId": "5ac2213e040ab15980c9b447",
            "emojiId": "004"
        }
    ]
    text_message = TextSendMessage(text='''$歡迎來到眉室$''', emojis=emoji)
    sticker_message = StickerSendMessage(
        package_id='446',
        sticker_id='1989'
    )

    iThome_logo_img = 'https://s4.itho.me/sites/default/files/images/ithome_logo.png'

    image_message = ImageSendMessage(
        original_content_url=iThome_logo_img,
        preview_image_url=iThome_logo_img
    )
    line_bot_api.reply_message(
        event.reply_token,
        [text_message, sticker_message, image_message])  #此陣列最多可加五種類型


def location_event(event):
    location_message = LocationSendMessage(
        title='台北車站',
        address='10041台北市中正區忠孝西路1段49號',
        latitude=25.0452399,
        longitude=121.51789
    )
    line_bot_api.reply_message(
        event.reply_token,
        location_message)


def other_event(event):
    text_message1 = TextSendMessage(text='抱歉，我不懂您的意思')
    line_bot_api.reply_message(
        event.reply_token,
        text_message1)