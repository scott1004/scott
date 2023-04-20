from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, StickerSendMessage, ImageSendMessage, LocationSendMessage,
    FollowEvent, UnfollowEvent, TemplateSendMessage, ImageCarouselTemplate, ImageCarouselColumn,
    PostbackAction, PostbackEvent, FlexSendMessage, ButtonsTemplate, QuickReply, QuickReplyButton, MessageAction,
    ConfirmTemplate, ButtonsTemplate, ButtonComponent, BubbleContainer, BoxComponent, TextComponent, URIAction,
    DatetimePickerAction, PostbackTemplateAction, MessageTemplateAction
)

line_bot_api = LineBotApi('T6/DxUN5kOosIOLqvXuRzcRUcPhNTHPkMTnFqcdPoSBIMqE7tyiq4maFqoClwAYv0uixE5pN4B/bkBV6FLtelfjn7nc/mSdZdntRC1dJAHFRm/TAV7TDmV9/lIQCbR/U7x53F7ntJUPaIhslcnSARQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('3f44551992490dccf3d09de1d82df23b')