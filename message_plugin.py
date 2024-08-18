import os

class Messanger:
    def __init__(self):
        """
        Потом загрузить html Messanger.load_html() (путь указыват при создании класса он запишется в self.path)\n
        Добавить что-то с помощью Messanger.change_html(type_, text, nuckname, style)\n
        Сохранить html с помощью Messanger.save_html()\n
        """
        self.html = ""
    
    def load_html(self):
        self.html = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chat</title>
</head>
<body>
    <!-- START BODY -->
    <!-- END BODY -->
<style>
    body, h3{
        padding: 0px;
        margin: 0px;
        font-family: Verdana, sans-serif;
        font-size: 16px;
        animation: scroll-down 1s ease-in-out infinite;
    }

    h3{
        padding-bottom: 5px;
    }

    .message{
        margin: 10px;
        padding: 15px;
        max-width: 40%;
        background-color: azure;
        border: 1px solid black;
        border-radius: 15px;
    }

    .my_message{
        color: green;
    }

    .friend_message{
        color: rgb(75, 0, 132);
    }

    .server_message{
        color: white;
        background-color: red;
        max-width: 100%;
        margin: 0px;
        margin-bottom: 0.2%;
        padding-left: 25px;
        padding-right: 25px;
        border-radius: 0px;
        text-align: center;
    }

    .client_message{
        color: red;
        background-color: rgb(244, 244, 244);
        max-width: 100%;
        margin: 0px;
        margin-bottom: 0.2%;
        padding-left: 25px;
        padding-right: 25px;
        border-radius: 0px;
        text-align: left;
    }
</style>
<script>
function getCount(parent, getChildrensChildren){
    var relevantChildren = 0;
    var children = parent.childNodes.length;
    for(var i=0; i < children; i++){
        if(parent.childNodes[i].nodeType != 3){
            if(getChildrensChildren)
                relevantChildren += getCount(parent.childNodes[i],true);
            relevantChildren++;
        }
    }
    return relevantChildren;
}
function scrollpage() {	
    var count = 0;
    var lastcount = 0
	function f() 
	{
        var count = document.querySelectorAll('div').length;
        if (lastcount != count){
		    window.scrollTo(0, 100000);
            lastcount = count;
        }
	    setTimeout( f, 0.05 );
	}f();
}
var Height=document.documentElement.scrollHeight;
var i=1,j=Height,status=0;
scrollpage();
</script>
</html>"""
    
    def save_html(self):
        with open("index.html", "w", encoding="utf-8") as htmlfile:
            htmlfile.write(self.html)
    
    def get_path(self, name="index.html"):
        return os.path.join(self.path, name)
    
    def add_server_msg(self, text):
        return f"""    <div class="message server_message"><h3>Server:</h3><span>{text}</span></div>"""

    def add_client_msg(self, text):
        return f"""    <div class="message server_message"><h3>Client:</h3><span>{text}</span></div>"""

    def add_myself_msg(self, text, nickname, style=None):
        return f"""    <div class="message my_message" {"" if style is None else "style=\""+style+"\""}><h3>{nickname}:</h3><span>{text}</span></div>"""

    def add_friend_msg(self, text, nickname, style=None):
        return f"""    <div class="message friend_message" {"" if style is None else "style=\""+style+"\""}><h3>{nickname}:</h3><span>{text}</span></div>"""

    def add_something(self, type_, text, nickname, style) -> str:
        if type_ == "server":
            return self.add_server_msg(text)
        elif type_ == "client":
            return self.add_client_msg(text)
        elif type_ == "friend":
            return self.add_friend_msg(text, nickname, style)
        elif type_ == "myself":
            return self.add_myself_msg(text, nickname, style)
        elif type_ == "clear":
            return ""
        else:
            raise Exception(f"MESSAGE_PLUGIN ERROR: type_={type_} is not in list")
    
    def change_html(self, type_: str, text: str, nickname: str = None, style: str = None) -> str:
        """
        1. type - тип (server, client, friend, myself)\n
        2. text - текст сообщения\n
        3. nickname - никнейм человека\n
        4. style - css стиль для строки, кастомит\n
        """
        text = self.add_something(type_, text, nickname, style)
        if text == "":
            self.clear()
            return self.html
        
        lines = self.html.split("\n")
        end_line = 0
        for line_id in range(len(lines)):
            if lines[line_id] == "    <!-- END BODY -->":
                end_line = line_id
                break

        lines.insert(end_line, text)
        self.html = "\n".join(lines)
        return self.html
    
    def clear(self):
        lines = self.html.split("\n")
        start_line = 0
        end_line = 0
        for line_id in range(len(lines)):
            if lines[line_id] == "    <!-- START BODY -->":
                start_line = line_id
            elif lines[line_id] == "    <!-- END BODY -->":
                end_line = line_id
                break
        lines = lines[:start_line+1] + lines[end_line:]
        self.html = "\n".join(lines)
        
