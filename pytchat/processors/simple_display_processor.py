from .chat_processor import ChatProcessor


class SimpleDisplayProcessor(ChatProcessor):

    def process(self, chat_components: list):
        chatlist = []
        timeout = 0

        if chat_components is None:
            return {"timeout": timeout, "chatlist": chatlist}
        for component in chat_components:
            timeout += component.get('timeout', 0)
            chatdata = component.get('chatdata')

            if chatdata is None:
                break
            for action in chatdata:
                if action is None:
                    continue
                if action.get('addChatItemAction') is None:
                    continue
                if action['addChatItemAction'].get('item') is None:
                    continue

                root = action['addChatItemAction']['item'].get(
                    'liveChatTextMessageRenderer')

                if root:
                    author_name = root['authorName']['simpleText']
                    message = self._parse_message(root.get('message'))
                    purchase_amount_text = ''
                else:
                    root = (action['addChatItemAction']['item'].get('liveChatPaidMessageRenderer')
                            or action['addChatItemAction']['item'].get('liveChatPaidStickerRenderer'))
                    if root:
                        author_name = root['authorName']['simpleText']
                        message = self._parse_message(root.get('message'))
                        purchase_amount_text = root['purchaseAmountText']['simpleText']
                    else:
                        continue
                chatlist.append(
                    f'[{author_name}]:  {message}  {purchase_amount_text}')
        return {"timeout": timeout, "chatlist": chatlist}

    def _parse_message(self, message):
        if message is None:
            return ''
        if message.get('simpleText'):
            return message['simpleText']
        elif message.get('runs'):
            runs = message['runs']
            tmp = ''
            for run in runs:
                if run.get('emoji'):
                    tmp += (run['emoji']['shortcuts'][0])
                elif run.get('text'):
                    tmp += (run['text'])
            return tmp
        else:
            return ''
