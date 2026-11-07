import os, re, sys
src, dst = sys.argv[1], sys.argv[2]
names = ["Home", "Ask", "Learn", "Verse", "Practice", "Explore"]
ORDER = [  # light value -> dark value, applied in order (longest/most specific first)
 ('background: #FFFFFF; border-radius: 18px; text-decoration: none; box-shadow', 'background: @@WHITE@@; border-radius: 18px; text-decoration: none; box-shadow'),
 ('rgba(242,246,247,0.96)', 'rgba(7,30,34,0.96)'), ('rgba(242,246,247,0)', 'rgba(7,30,34,0)'),
 ('rgba(255,255,255,0.96)', 'rgba(10,36,40,0.97)'),
 ('#F2F6F7', '#071E22'),
 ('background: #E9A845;', 'background: #7A5A1E;'),
 ('background: #EBC27A;', 'background: #5C4E22;'), ('background: #D3C7AE;', 'background: #28555A;'), ('background: #E0D7C4;', 'background: #21494E;'),
 ('background: #FFFFFF', 'background: #0C2A2F'),
 ('#E3EFEC', '#154045'), ('#E6EEF0', '#10353A'), ('#E3F1EE', '#10353A'), ('#BFDDD7', '#1F5A5F'),
 ('#DDE6E8', '#1D4247'), ('#CBD6D9', '#2A5357'),
 ('background: #0F5257', 'background: #2A8C82'), ('box-shadow: inset 0 0 0 1.5px #0F5257', 'box-shadow: inset 0 0 0 1.5px #86CDC2'),
 ('#0F5257', '#86CDC2'),
 ('#1E2B3A', '#E4EFEC'), ('#2F3C42', '#D5E4E1'), ('#3D4A50', '#D5E4E1'),
 ('#5D6B70', '#9DB6B3'), ('#67777C', '#9DB6B3'), ('#9AA3A6', '#6F8E8B'),
 ('#DDEFEC', '#10353A'), ('#0B3F43', '#86CDC2'),
 ('#E6EEFB', '#16274A'), ('#1F3A6E', '#B5CBF5'), ('#EEE7F6', '#251B3B'), ('#3E2C63', '#D3C0F2'),
 ('#FBE9C6', '#3A3015'), ('#8A5A12', '#E9D58A'),
 ('rgba(255,255,255,0.55)', 'rgba(255,255,255,0.08)'),
 ('@@WHITE@@', '#FFFFFF'),
]
for n in names:
    s = open(os.path.join(src, "P%s.dc.html" % n), encoding="utf-8").read()
    head, sep, tail = s.partition('<script type="text/x-dc"')
    for a, b in ORDER:
        head = head.replace(a, b)
        tail = tail.replace(a, b)
    # the home ask box stays white, as in production; its placeholder and button keep their colours
    head = head.replace('<span style="flex-grow: 1; text-align: left; font-size: 17px; color: #7A8790;">', '<span style="flex-grow: 1; text-align: left; font-size: 17px; color: #6B7A80;">')
    s = head + sep + tail
    s = re.sub(r'href="P(Home|Ask|Learn|Verse|Practice|Explore)\.dc\.html"', r'href="D\1.dc.html"', s)
    s = s.replace("<title>", "<title>Dark: ", 1)
    # colour switch in the dark files leads to the light twin
    s = re.sub(r'href="D(\w+)\.dc\.html" data-toggle="theme" aria-label="Switch to Dark colours"', r'href="P\1.dc.html" data-toggle="theme" aria-label="Switch to Light colours"', s)
    s = s.replace('<path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"></path>',
                  '<circle cx="12" cy="12" r="4.2" fill="none" stroke="currentColor" stroke-width="2"></circle><path d="M12 2.5v2.2M12 19.3v2.2M2.5 12h2.2M19.3 12h2.2M5.3 5.3l1.6 1.6M17.1 17.1l1.6 1.6M5.3 18.7l1.6-1.6M17.1 6.9l1.6-1.6" stroke="currentColor" stroke-width="2" stroke-linecap="round"></path>')
    s = s.replace('</svg></span>Dark</a>', '</svg></span>Light</a>')
    open(os.path.join(dst, "D%s.dc.html" % n), "w", encoding="utf-8").write(s)
print("ok")
