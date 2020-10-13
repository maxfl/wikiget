# wikiget - CLI tool for downloading files from Wikimedia sites
# Copyright (C) 2018, 2019, 2020 Cody Logan and contributors
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Wikiget is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Wikiget is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Wikiget. If not, see <https://www.gnu.org/licenses/>.

from .dl import parse_url, get_site
import re

header_regex          = re.compile(r'^(=+)\s*(\w(\w| )*)\s*\1\s*$', re.I)
gallery_start_regex   = re.compile(r'^<gallery[^>]*>\s*$', re.I)
gallery_caption_regex = re.compile(r'caption="((\w| )+)"', re.I)
gallery_end_regex     = re.compile(r'^</gallery[^>]*>\s*$', re.I)

file_gallery_regex    = re.compile(r'^(?:File:|Image:)([^/\r\n\t\f\v|]+\.\w+)\s*(?:\|\s*(\w(?:\w| )*))?$', re.I)
file_regex            = re.compile(r'\[\[(?:File:|Image:)([^/\r\n\t\f\v|]+\.\w+)\s*(?:\|\a+)*?\s*(?:\|\s*([^|]+))*\s*\]\]')
# [[File:Northrend.svg|thumb|Northrend]]

class WikiPageParser(object):
    in_gallery=False
    current_depth=0
    def __init__(self):
        pass

    def parse(self, text):
        for line in text.splitlines():
            self.parse_line(line)

    def parse_line(self, line):
        if self.check_header(line): return
        if self.check_gallery(line): return

        if self.in_gallery:
            self.check_media_gallery(line)
        else:
            self.check_media(line)

    def check_media(self, line):
        match = file_regex.search(line)

        if not match: return

        filename = match.group(1)
        caption  = match.group(2)

        print('    filename:', filename)
        if caption:
            print('        caption:', caption)

    def check_media_gallery(self, line):
        match = file_gallery_regex.search(line)

        if not match: return

        filename = match.group(1)
        caption  = match.group(2)

        print('    filename:', filename)
        if caption:
            print('        caption:', caption)

    def check_header(self, line):
        header = header_regex.search(line)

        if not header:
            return False

        depth = len(header.group(1))
        title = header.group(2)
        if self.current_depth>depth:
            print('   level up...')
        print(f'Section {depth}: {title}')
        self.current_depth = depth

        return True

    def check_gallery(self, line):
        gallery_start = gallery_start_regex.search(line)
        if gallery_start:
            caption = gallery_caption_regex.search(line)
            if caption:
                caption = caption.group(1)
                print(f'Gallery: {caption}')
            else:
                print(f'Gallery')
            self.in_gallery = True
            return True

        if self.in_gallery:
            gallery_end = gallery_end_regex.search(line)
            if gallery_end:
                print('    end gallery...')
                self.in_gallery = False
                return True

        return False

def extract(args):
    site_name, filename = parse_url(args.FILE, args, filetype='page')
    site = get_site(site_name, args)
    page = site.pages[filename]
    if not page.exists:
        print("Page {} does not exist".format(filename))
    text = page.text()

    parser = WikiPageParser()
    parser.parse(text)


