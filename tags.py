def formula(obj):
    """
    Визуализация зубов пациентов для стоматологий
    """
    def get_obj(*sector):
        return [n for n in obj.diseases if n.sector.slug in sector]

    colors = {
        'gum': '#ffffff',
        'white': '#ffffff',
        'body': '#dee1e9',
    }
    ns = {
        'xmlns': "http://www.w3.org/2000/svg",
        'inkscape': "http://www.inkscape.org/namespaces/inkscape",
        'sodipodi': "http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd",
    }
    width = 55
    height = 150

    ET.register_namespace('', "http://www.w3.org/2000/svg")
    root = ET.Element('svg', width=str(width), height=str(height), viewBox=f"0 0 {width} {height}", )

    # GUM
    gum = ET.SubElement(root, 'rect', rx='5', ry='5', width=str(width), height='70', fill=colors['gum'])
    gum.attrib['class'] = 'formula-gum'
    gum.attrib['data-sector'] = 'gum'
    if get_obj('gum'):
        # задаем цвет из БД если есть болезнь десен
        gum.attrib['fill'] = get_obj('gum')[0].disease.color

    # SIDE
    side_root = ET.SubElement(root, 'g')
    side_root.attrib['class'] = 'formula-side'
    side_root.attrib['data-sector'] = 'side'
    side_parse = ET.parse(f'{settings.BASE_DIR}/teeth/tmpl.svg')
    side_parse_getroot = side_parse.getroot()

    side_attrib = {}
    if get_obj('side'):
        side_root.attrib['title'] = get_obj('side')[0].sector.tt
        if get_obj('side')[0].disease.svg:
            for n in get_obj('side')[0].disease.svg.split('\r\n'):
                attribs = n.split('+')
                props = {}
                if len(attribs) > 1:
                    for xx in attribs[1].split(';'):
                        xx.split(':')[0]
                        props[xx.split(':')[0]] = xx.split(':')[1]
                side_attrib[attribs[0]] = props
        else:
            side_default_color = get_obj('side')[0].disease.color
            side_attrib['body'] = {'fill': side_default_color}
            side_attrib['head'] = {'fill': side_default_color, 'stroke': colors['body']}
    else:
        side_attrib['body'] = {'transform-origin': 'center'}
        side_attrib['head'] = {'fill': colors['white'], 'stroke': colors['body']}

    for k, v in side_attrib.items():
        side_scale_x = 1
        side_scale_y = 1
        side_transform_x = 0
        side_transform_y = 0
        if not obj.is_left():
            # зекралим по x все правые
            side_scale_x = '-1'
        if not obj.is_upper():
            # зеркалим по y все нижние, если не из списка
            if not k in ['body', 'head', 'channel', 'channel-half', 'periodontit']:
                side_scale_y = '-1'
            else:
                # сдвигаем нижние те что из списка вниз на 55px
                side_transform_y = '55'
            if 'y' in v:
                # вместо transform в админке y
                side_transform_y = int(v['y']) * int(side_scale_y)
        side_attrib[k].update({
            'y': '',
            'transform-origin': 'center',
            'transform': f'translate({side_transform_x}, {side_transform_y}) scale({side_scale_x}, {side_scale_y})',
        })
    side_common_props = {
        'corona-in': {'fill': colors['body']},
        'channel-half': {'fill': '#8889be'},
        'periodontit': {'fill': '#ff0000'}
    }
    for k, v in side_common_props.items():
        if k in side_attrib:
            side_attrib[k].update(v)

    side_tmpl = side_parse_getroot.find(f".//*[@id='{obj.tmpl}']")
    side_g_id = []
    if side_tmpl:
        side_g_id = [(side_tmpl.find(f".//*[@inkscape:label='{k}']", ns), v) for k, v in side_attrib.items()]
    side_g_common = [(side_parse_getroot.find(".//*[@id='common']").find(f".//*[@inkscape:label='{k}']", ns), v) for k, v in side_attrib.items()]
    side_g_l = side_g_id + side_g_common

    for n in side_g_l:
        if n[0]:
            # Там где есть transform удаляем
            if 'transform' in n[0].attrib:
                del n[0].attrib['transform']
            # Выбираем только один! path
            side_paths = n[0].findall('.//xmlns:path', ns)
            for side_path in side_paths:
                if 'style' in side_path.attrib:
                    del side_path.attrib['style']
                # Добавляем свойства к path
                for k, v in n[1].items():
                    side_path.attrib[k] = v
                side_root.append(side_path)

    # OVER
    if obj.is_front():
        over_exclude = ['omidl', 'omidr']
    else:
        over_exclude = ['omid']
    over_g = side_parse_getroot.find(".//*[@id='over']")
    
    for n in over_g.findall(".//*[@data-sector]"):
        n.attrib['class'] = 'formula-in'
        if n.attrib['data-sector'] in over_exclude:
            over_g.remove(n)

    for n in get_obj('otop', 'omid', 'omidl', 'omidr', 'obottom', 'oleft', 'oright'):
        over_g.find(f".//*[@data-sector='{n.sector.slug}']/xmlns:path", ns).attrib['fill'] = n.disease.color
