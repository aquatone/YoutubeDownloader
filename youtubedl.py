#!/usr/bin/python

# youtubedl.py
#
# Youtube downloader!!
# Download youtube videos and/or playlists.
#
# Usage:
#    python youtubedl.py --help
# 
# ~ aquat0n3 (aquatone06@gmail.com, kny8mare@gmail.com)
# gr33tz: andy.fast0w

import sys
import re
import urllib
import urlparse
import os

# formats and corresponding itag values
fmts = {
        13:('.3gp', '3gp Low 144p'),
        17:('.3gp', '3gp Med 144p'),
        36:('.3gp', '3gp Hi 240p'),
        5:('.flv', 'Flv Low 240p'),
        34:('.flv', 'Flv Med 360p'),
        6:('.flv', 'Flv Med2 360p'),
        35:('.flv', 'Flv Hi 480p'),
        43:('.webm', 'webm 480p'),
        44:('.webm', 'webm HD 720p'),
        45:('.webm', 'webm HD2 720p'),
        46:('.webm', 'webm HD3 1080p'),
        18:('.mp4', 'mp4 Hi 360p'),
        22:('.mp4', 'mp4 HD 720p'),
        37:('.mp4', 'mp4 HD2 1080p'),
        38:('.mp4', 'mp4 HD3 3072p')
        }

# video quality higher to lower (?maybe)
fmt_priority = [38, 37, 22, 18, 46, 45, 44, 43, 35, 6, 34, 5, 36, 17, 13]


# youtubedl
# Function downloads the video (of a particular format) corresponding to the passed url.
# @@param youtube_url url to parse
# @@param fout_name output filename or blank (for autogen)
# @@param quality preffered output quality (download the next best, if not available)
def youtubedl(youtube_url, fout_name='', quality=0):
    '''
    Function downloads video from youtube_url and stores it in
    file fout_name
    '''

    print '[+] Fetching URL:', youtube_url
    
    # Extract video id and query video info
    video_id = re.search(r'(?i)watch\?.*v=([^\&]*).*', youtube_url).group(1)
    
    video_info = urlparse.parse_qs(
                                urllib.urlopen(r'http://www.youtube.com/get_video_info?video_id='
                                    + video_id
                                    + "&asv=3&el=detailpage&hl=en_US"
                                    ).read()
                                )

    # Check if video info is locked (hence cannot fetch using this method)
    if video_info['status'][0].lower() != 'ok':
        print '[!] Unable to fetch video info'
        return

    # Retrieve video title
    video_title = video_info['title'][0]
    print '[+] Video Title: ' + video_title

    #----------------------------------- Print download options ----------------------------------------#
    # Retrieve available formats and download urls
    video_list = {}
    for video in video_info['url_encoded_fmt_stream_map'][0].split(','):
        v = urlparse.parse_qs(video)
        video_list[int(v['itag'][0])] = v['url'][0] + '&signature=' + v['sig'][0]

    choice = 0
    if quality <= 0:    # if no format specified
        while 1:
            print '[?] Choose format:'
            for fmt in fmt_priority:
                if fmt in video_list.keys():
                    print '\t[%2d] %s' % (fmt, fmts[fmt][1])

            try:
                choice = int(raw_input('\tChoice? '))
                if choice in video_list.keys():
                    break
            except:
                pass
            
    else:
            try:
                i = fmt_priority.index(quality)
            except ValueError:
                print '[!] Invalid video quality selected, choosing highest available'
                i = 0
            
            for fmt in fmt_priority[i:]:
                if fmt in video_list.keys():
                    choice = fmt
                    break
            else:
                for fmt in (fmt_priority[:i])[::-1]:
                    if fmt in video_list.keys():
                        choice = fmt
                        break
            
    #---------------------------------------------------------------------------------------------------#
   

    # Download the file
    fout_name = fout_name if fout_name != '' else video_title
    fout_name = re.sub(r'[^A-Za-z0-9-_.]+', ' ', fout_name)
    fout_name = fout_name + fmts[choice][0]
    print '[+] Downloading: [' + fmts[choice][1] + ']'
    #print '[>] Link: ' + video_list[choice]

    if os.path.exists(fout_name):
        print '[!] \"%s\" already exists on disk, skipping!' % (fout_name, )
    else:
        urllib.urlretrieve(video_list[choice], fout_name, reporthook=download_progress)
        print '\n[+] Done !'



def download_progress(count, block_size, total_size):
    
    percent = int( (count*block_size*100)/total_size )
    sys.stdout.write("\r[" + '#' * (percent/2) + '-' * (50 - percent/2)  + "] %3d%% of %d MB" % (percent, total_size/(1024 * 1024)) )


# Checks if the url is a youtube video link
# or a playlist - and calls the appropriate handler
def parse_url(y_url, f_name, quality):

    if re.search(r'(?i)www\.youtube\.com/playlist\?list=', y_url):
        # Parse playlist
        parse_playlist(y_url, quality)
        
    elif re.search(r'(?i)www\.youtube\.com/watch\?v=', y_url):
        # Parse and download video
        youtubedl(y_url, f_name, quality)

    else:
        print '[!] Invalid URL: "%s" skipping !' % y_url
        return


# Parses a youtube playlist for video links and downloads them
def parse_playlist(y_url, quality):
    
    pl_id = re.findall('\?list=PL([^&]+)', y_url)[0]
    pl_data = urllib.urlopen(y_url).read()
    pl_videos = re.findall(r'<[^\<]*(/watch\?v=[^&]+)&amp;list=.{2}' + pl_id + '[^\>]*tile-link-block', pl_data)
    
    print '[+] Downloading %d videos from playlist "%s"\n' % (len(pl_videos), pl_id)
    for vid in pl_videos:
        youtubedl(vid, '', quality)
        print
    



if __name__ == '__main__':

    from optparse import OptionParser

    class MyParser(OptionParser):
        def format_epilog(self, formatter):
            return self.epilog
        def format_description(self, formatter):
            return self.description
        
    usage = "usage: %prog [options] [youtube video/playlist URL]"
    parser = MyParser(usage=usage)
    
    parser.add_option("-f", "--file", dest="infile",
                      help="Read video/playlist URLs from FILE",
                      default= "", metavar="FILE")
    
    parser.add_option("-o", "--out", dest="outfile",
                      help="Output filename (only for single url mode)",
                      default="", metavar="FILE")
    
    parser.add_option("-q", "--quality",
                      dest="quality", type="int", metavar="CODE", default=-1,
                      help="Try to fetch videos of this quality (if available)")
    
    parser.description = 'Youtube video / playlist downloader\n' +\
                         '\tkny8mare@gmail.com\n'
    parser.epilog = "\tQuality codes:\n" + '\n'.join(['\t\t' + str(key) + '\t' + fmts[key][1] for key in fmt_priority])
    parser.epilog += "\nExample:" + \
                     "\n\tpython youtubedl.py http://www.youtube.com/watch?v=UtPTvyjtx3g" + \
                     "\n\tpython youtubedl.py http://www.youtube.com/playlist?list=PLB8BD27D78788791D -q 38" + \
                     "\n\tpython youtubedl.py -f url_list.txt -q 38\n"
    
    (options, args) = parser.parse_args()
    
    
    # ----------- reading URLs from a file --------
    if options.infile != '':
        url_list = open(options.infile).read().splitlines()
        for y_url in url_list:
            parse_url(y_url, '', options.quality)
            print        

    # ---------- single URL specified in cmdline ------
    elif len(args) != 0:
        y_url = args[0]
        parse_url(y_url, options.outfile, options.quality)

    else:
        parser.print_help()
