
import os
import re
import sys


lines = []
for line in sys.stdin:
    lines.append(line)

# 去掉头三行
lines = lines[3:]

key = 'README'
ret = {}

for line in lines:

    # line = line.strip()
    # 去掉行尾的换行
    line = re.sub(r'\n$', '', line)

    # 转义 |
    line = re.sub(r'\\\|', '&#124;', line)

    # 分页
    if line == '<a name="Wechaty"></a>': # ('## Wechaty'):
        key = 'wechaty'
    if line == '## Friendship':
        key = 'friendship'
    if line == '## Room':
        key = 'room'
    if line == '## Message':
        key = 'message'
    if line == '## Contact':
        key = 'contact'
    if line == '<a name="WechatyEventName"></a>':
        key = 'README'

    if line.startswith('#'):
        # 把标题中的链接去掉，因为docsify支持不好
        if '~~' in line:
            # line = re.sub(r' ⇒ \[<code>([^<]+)</code>\]\(([^\)]+)\)(.*)', '~~\n\n**Return the type of**: [\\1](\\2) \\3\n\n', line)
            # line = re.sub(r' ⇒ <code>([^<]+)</code>(.*)', '~~\n\n**Return the type of**: \\1 \\2\n\n', line)
            line = re.sub(r' ⇒ (.+)', '~~\n\n**Return the type of**: \\1\n\n', line)
            line = line[:-2]
        else:
            # line = re.sub(r' ⇒ \[<code>([^<]+)</code>\]\(([^\)]+)\)(.*)', '\n\n**Return the type of**: [\\1](\\2) \\3\n\n', line)
            # line = re.sub(r' ⇒ <code>([^<]+)</code>(.*)', '\n\n**Return the type of**: \\1 \\2\n\n', line)
            line = re.sub(r' ⇒ (.+)', '\n\n**Return the type of**: \\1\n\n', line)
    
    if ' ⇒' in line:
        line = line.replace(' ⇒', '')
    
    if '# ~~' in line and line.startswith('#') and not line.endswith('~~'):
        line = line.strip() + '~~'

    # 把这样markdown里的加号+去掉
    # * [.payload](#Message+payload)
    # line = re.sub(r'\]\(([^\+]+)\+([^\+]+)\)', '](\\1\\2)', line)
    def replace_markdown_link(x):
        a, b = x.groups()
        a = a.replace('&#41;', ')')
        a = a.replace('&#93;', ']')

        b = b.replace('+', '')
        b = b.replace('.', '')
        b = b.replace(' ', '')
        aa = re.findall(r'\(([^\)]+)\)', a)
        if aa:
            c = aa[0]
            c = re.sub(r'\(|\)|\[|\{|\]|\}|\+|\.', '', c)
            c = c.replace(',', '-')
            b += c
        b = b.replace(' ', '')
        r = '[{}]({})'.format(a, b)
        # if 'say' in line:
        #     print('a', line, a, b, r)
        #     print(x.groups())
        return r
    line = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', replace_markdown_link, line.replace('])](', '&#93;&#41;]('))

    # 替换几个主类的链接
    line = re.sub(r'<a href="#Wechaty">Wechaty</a>', '[Wechaty](/api/wechaty?id=top)', line)
    line = re.sub(r'<a href="#Friendship">Friendship</a>', '[Friendship](/api/friendship?id=top)', line)
    line = re.sub(r'<a href="#Message">Message</a>', '[Message](/api/message?id=top)', line)
    line = re.sub(r'<a href="#Contact">Contact</a>', '[Contact](/api/contact?id=top)', line)
    line = re.sub(r'<a href="#Room">Room</a>', '[Room](/api/room?id=top)', line)
    
    if key not in ret:
        ret[key] = []
    
    ret[key].append(line)


# 找到类型定义
typedefs = re.findall(r'<dt><a href="#([^"]+)">[^<]+</a></dt>', '\n'.join(ret['README']))
for key in ret.keys():
    for t in typedefs:
        s = '<dt><a href="#{}">{}</a></dt>'.format(t, t)
        d = '[{}](/api/?id={})'.format(t, t.lower())
        ret[key] = [
            re.sub(s, d, l)
            for l in ret[key]
        ]
        s = '\\(#{}\\)'.format(t)
        d = '(/api/?id={})'.format(t.lower())
        ret[key] = [
            re.sub(s, d, l)
            for l in ret[key]
        ]


keys = [
    'README',
    'wechaty',
    'contact',
    'friendship',
    'room',
    'message'
]

for key in keys:
    ret[key] = '\n'.join(ret[key])

output_dir = './src/api'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

zh_output_dir = './src/zh_api'
if not os.path.exists(zh_output_dir):
    os.makedirs(zh_output_dir)

def replace(text):
    replace_list = [
        ['(#Message)', '(/api/message?id=top)'],
        ['(#Room)', '(/api/room?id=top)'],
        ['(#Contact)', '(/api/contact?id=top)'],
        ['(#Wechaty)', '(/api/wechaty?id=top)'],
        ['(#Friendship)', '(/api/friendship?id=top)'],
    ]
    
    for a, b in replace_list:
        text = text.replace(a, b)
    
    return text

for key in keys:
    for od in (output_dir, zh_output_dir):
        path = os.path.join(od, key + '.md')
        content = ret[key]
        if key == 'README':
            content = open('api.md').read() + '\n\n' + content

        content = re.sub(r'^##\s', '# ', content)
        content = re.sub(r'^###\s', '## ', content)
        content = re.sub(r'^####\s', '### ', content)
        content = re.sub(r'^#####\s', '#### ', content)
        content = re.sub(r'\n##\s', '\n# ', content)
        content = re.sub(r'\n###\s', '\n## ', content)
        content = re.sub(r'\n####\s', '\n### ', content)
        content = re.sub(r'\n#####\s', '\n#### ', content)
        content = replace(content)

        with open(path, 'w') as fp:
            if 'zh' in od:
                content = content.replace('/api/', '/zh/api/')
                for c in ('Wechaty', 'Friendship', 'Contact', 'Message', 'Room'):
                    content = content.replace('## ' + c + '\n', '## ' + c + '类\n')
                    content = content.replace('# ' + c + '\n', '# ' + c + '类\n')
            fp.write(content)

print('ok', len(lines))