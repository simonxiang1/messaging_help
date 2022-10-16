''' Facebook Messenger Chat Parser Version 1.0.0 - Designed on 11.04.18 by
 /$$   /$$             /$$                     /$$$$$$$                                                      /$$
| $$$ | $$            | $$                    | $$__  $$                                                    | $$
| $$$$| $$  /$$$$$$  /$$$$$$    /$$$$$$       | $$  \ $$ /$$   /$$  /$$$$$$   /$$$$$$   /$$$$$$   /$$$$$$  /$$$$$$
| $$ $$ $$ |____  $$|_  $$_/   /$$__  $$      | $$$$$$$/| $$  | $$ /$$__  $$ /$$__  $$ /$$__  $$ /$$__  $$|_  $$_/
| $$  $$$$  /$$$$$$$  | $$    | $$$$$$$$      | $$__  $$| $$  | $$| $$  \ $$| $$  \ $$| $$$$$$$$| $$  \__/  | $$
| $$\  $$$ /$$__  $$  | $$ /$$| $$_____/      | $$  \ $$| $$  | $$| $$  | $$| $$  | $$| $$_____/| $$        | $$ /$$
| $$ \  $$|  $$$$$$$  |  $$$$/|  $$$$$$$      | $$  | $$|  $$$$$$/| $$$$$$$/| $$$$$$$/|  $$$$$$$| $$        |  $$$$/
|__/  \__/ \_______/   \___/   \_______/      |__/  |__/ \______/ | $$____/ | $$____/  \_______/|__/         \___/
                                                                  | $$      | $$
                                                                  | $$      | $$
                                                                  |__/      |__/

Please see the README.md file for help in running this file. TLDR; Give put a message.html file in the same directory and it will output a text file with messenge stats
'''


from bs4 import BeautifulSoup as soup
import re
from collections import Counter


def main(messenger_chat):
    print('Nate\'s Messenger (Facebook) Chat Parser - Version 1.0.0')

    try:
        print('\nPlease wait while the document loads... For large files this could take upwards of several minutes...')
        with open('message.html') as html:
            file = soup(html, 'html.parser')
        print('File has finished loading. Parsing data...\n')
    except FileNotFoundError:
        print('Error! File not found. You must give me a message.html file to work with from Facebook Messenger!')
        return None

    # Get the current title
    currentTitle = file.title.string

    # Tell the user analysis has begun
    print('Performing analysis on {0}...'.format(currentTitle))

    # Navigate to where messenger stores messages
    parser = file.body.div.div.div.contents[1].contents[1]

    # Organizes the participants
    parse_participants(parser.div.div.string)

    # Get the messages and sets the chat's total messages
    messages = parser.contents[1:]
    messenger_chat['total_messages'] = len(messages)

    # print('\nWriting messages to a file... ({0})'.format(len(messages)))
        # message.write(str(messages))

    print('\nParsing Chat Messages... ({0})'.format(len(messages)))

    # Iterate through all messages and parse data
    with open("parsed_messages.txt", "w") as message:
        for i, msg in enumerate(messages):
            content = msg.contents
            print("Writing message "+str(i)+" to the file...\n")
            message.write(str(content)+"\n")

    for message in messages:
        content = message.contents

        payload = {
            'user': content[0].string,
            'message': content[1].div.contents[1].string,
            'date': content[2].string,
        }

        # Increase User's total message count
        try:
            messenger_chat['members'][payload['user']]['total_messages'] += 1
        except KeyError:
            #print("Error! Discovered Missing User! (User {0})".format(payload['user']))
            continue  # Skip Loop for this Individual
        # Parse through for images and videos and Find and parse links sent in the chat
        # If finds media, ignore the message (usually just "User sent a photo")
        if not parse_media(payload, message) and not parse_links(payload, message):
            # Parse through the words
            if not parse_words(payload):
                # If the message is not None/empty, fix the mesage with no linebreak (</br>) statements
                if not content[1].div.contents[1]:
                    message = ''
                    for item in content[1].div.contents[1].contents:
                        if isinstance(item, str):
                            message += item
                    payload['message'] = message
                    if not parse_words(payload):
                        print("A Secondary Parse Failed... :(")
        # Parse through the reactions
        #parse_reactions(payload, message)

    print("Done! Analysis was successful!")
    print('\nWriting to file anaylsis results...')

    # Give a usable list in console and write to file
    with open('messenger_stats.txt', 'w') as f:
        # Header
        f.write('File Generated Using Nate\'s Messenger Parser (https://github.com/artyomos/messenger-parser)\nVersion 1.0.0\n\n')

        # Group Chat Title
        f.write('Messenger Chat: {0}\n\n'.format(currentTitle))

        # Stats
        f.write('Total Messages: {0}\n'.format(
            messenger_chat['total_messages']))
        f.write('Word Count: {0}\n'.format(messenger_chat['word_count']))
        f.write('Character Count: {0}\n'.format(
            messenger_chat['character_count']))
        f.write('Images Sent: {0}\n'.format(messenger_chat['image_count']))
        f.write('Gifs Sent: {0}\n'.format(messenger_chat['gif_count']))
        f.write('Videos Sent: {0}\n'.format(messenger_chat['video_count']))
        f.write('Audio Files Sent: {0}\n'.format(
            messenger_chat['audio_count']))
        f.write('Links Sent: {0}\n'.format(messenger_chat['link_count']))
        f.write('Reactions Given: {0}\n'.format(
            messenger_chat['reaction_count']['given']))
        for reaction in messenger_chat['reaction_count']['reaction_counter']:
            f.write('\t{0}:{1}'.format(
                reaction, messenger_chat['reaction_count']['reaction_counter'][reaction]))

        f.write('\nThe 50 Most Common Words:\n')
        words = remove_common(messenger_chat['words_counter']).most_common(50)
        for num in range(len(words)):
            f.write('\t{0}. {1} ({2}x / {3:.2f}%)'.format(
                num + 1, words[num][0], words[num][1], words[num][1]/messenger_chat['word_count']*100))
            if num % 3 == 0 and num != 0:
                f.write('\n')

        # User Stats
        f.write('\n\nStats by Member:')
        for user in messenger_chat['members']:
            individual = messenger_chat['members'][user]
            f.write('\n\n{0}\n\n'.format(user))
            f.write('Total Messages: {0} ({1:.2f}%)\n'.format(
                individual['total_messages'], (individual['total_messages'] / messenger_chat['total_messages'] * 100)))
            f.write('Word Count: {0} ({1:.2f}%)\n'.format(
                individual['word_count'], (individual['word_count'] / messenger_chat['word_count'] * 100)))
            f.write('Character Count: {0} ({1:.2f}%)\n'.format(
                individual['character_count'], (individual['character_count'] / messenger_chat['character_count'] * 100)))
            f.write('Images Sent: {0} ({1:.2f}%)\n'.format(
                individual['image_count'],  (individual['image_count'] / messenger_chat['image_count'] * 100)))
            #f.write('Gifs Sent: {0} ({1:.2f}%)\n'.format(
                #individual['gif_count'], (individual['gif_count'] / messenger_chat['gif_count'] * 100)))
            f.write('Videos Sent: {0} ({1:.2f}%)\n'.format(
                individual['video_count'], (individual['video_count'] / messenger_chat['video_count'] * 100)))
            f.write('Audio Files Sent: {0} ({1:.2f}%)\n'.format(
                individual['audio_count'], (individual['audio_count'] / messenger_chat['audio_count'] * 100)))
            f.write('Links Sent: {0} ({1:.2f}%)\n'.format(
                individual['link_count'], (individual['link_count'] / messenger_chat['link_count'] * 100)))
            f.write('Reactions Given: {0} ({1:.2f}%)\n'.format(
                individual['reaction_count']['given'], (individual['reaction_count']['given'] / messenger_chat['reaction_count']['given'] * 100)))
            for reaction in individual['reaction_count']['given_counter']:
                f.write('\t{0}:{1}'.format(
                    reaction, individual['reaction_count']['given_counter'][reaction]))
            f.write('\nReactions Received: {0} ({1:.2f}%)\n'.format(
                individual['reaction_count']['received'], (individual['reaction_count']['received'] / messenger_chat['reaction_count']['given'] * 100)))
            for reaction in individual['reaction_count']['received_counter']:
                f.write('\t{0}:{1}'.format(
                    reaction, individual['reaction_count']['received_counter'][reaction]))
            f.write('\nThe 25 Most Common Words:\n')
            words = remove_common(individual['words_counter']).most_common(25)
            for num in range(len(words)):
                f.write('\t{0}. {1} ({2}x / {3:.2f}%)'.format(
                    num + 1, words[num][0], words[num][1], words[num][1]/individual['word_count']*100))
                if num % 3 == 0 and num != 0:
                    f.write('\n')
    print('Wrote Results to messenger_stats.txt. Please check that file for details!\n\nThanks for using my program :)!')


def remove_common(counter):
    # Common useless messenger words
    common_words = ['all', 'just', 'being', 'over', 'both', 'through', 'yourselves', 'its', 'before', 'herself', 'had', 'should', 'to', 'only', 'under', 'ours', 'has',
     'do', 'them', 'his', 'very', 'they', 'not', 'during', 'now', 'him', 'nor', 'did', 'this', 'she', 'each', 'further', 'where', 'few', 'because', 'doing', 'some',
      'are', 'our', 'ourselves', 'out', 'what', 'for', 'while', 'does', 'above', 'between', 't', 'be', 'we', 'who', 'were', 'here', 'hers', 'by', 'on', 'about',
       'of', 'against', 's', 'or', 'own', 'into', 'yourself', 'down', 'your', 'from', 'her', 'their', 'there', 'been', 'whom', 'too', 'themselves', 'was', 'until',
        'more', 'himself', 'that', 'but', 'don', 'with', 'than', 'those', 'he', 'me', 'myself', 'these', 'up', 'will', 'below', 'can', 'theirs', 'my', 'and', 'then',
         'is', 'am', 'it', 'an', 'as', 'itself', 'at', 'have', 'in', 'any', 'if', 'again', 'no', 'when', 'same', 'how', 'other', 'which', 'you', 'after',
          'most', 'such', 'why', 'a', 'off', 'i', 'yours', 'so', 'the', 'having', 'once', 'm', 'll', 'didn', 't']
    for word in common_words:
        del counter[(word.capitalize())]
    return counter


def parse_words(payload):
    try:
        words = re.findall(r'\w+', payload['message'])
        words = [word.title() for word in words]
        messenger_chat['words_counter'].update(words)
        messenger_chat['word_count'] += len(words)
        messenger_chat['character_count'] += len(''.join(words))
        user = messenger_chat['members'][payload['user']]
        user['words_counter'].update(words)
        user['word_count'] += len(words)
        user['character_count'] += len(''.join(words))
    except TypeError:
        if payload['message'] is not None:
            print('Error: TimeStamp of {0}'.format(payload['date']))
            print('Message: "{0}"'.format(payload['message']))
        return False
    except KeyError:
        print("Discovered person who left chat!")
        return False
    return True


def parse_media(payload, message):
    user = messenger_chat['members'][payload['user']]
    images = message.find_all('img')
    if images:
        for image in images:
            # If image is a gif
            if image['src'][-3:] == 'gif':
                messenger_chat['gif_count'] += 1
                user['gif_count'] += 1
            else:
                messenger_chat['image_count'] += 1
                user['image_count'] += 1
    videos = message.find_all('video')
    if videos:
        messenger_chat['video_count'] += len(videos)
        user['video_count'] += len(videos)
    audio = message.find_all('audio')
    if audio:
        messenger_chat['audio_count'] += len(audio)
        user['audio_count'] += len(audio)
    if images or audio or videos:
        return True
    return False


def parse_links(payload, message):
    user = messenger_chat['members'][payload['user']]
    links = message.find_all('a')
    if links:
        for link in links:
            if link['href'][:4] == 'http':
                messenger_chat['link_count'] += 1
                user['link_count'] += 1
        return True


def parse_participants(members):
    # Remove useless messenger strings
    members = members.replace('Participants:', '')
    members = members.replace(' and ', ', ')
    members = members.strip().split(', ')
    # Add Member to members
    for participant in members:
        messenger_chat['members'][participant] = {
            'total_messages': 0,
            'word_count': 0,
            'character_count': 0,
            'image_count': 0,
            'gif_count': 0,
            'video_count': 0,
            'audio_count': 0,
            'link_count': 0,
            'reaction_count': {
                'given': 0,
                'received': 0,
                'given_counter': Counter(),
                'received_counter': Counter(),
            },
            'other': {
                'like_usage': 0,
                'emoji_usage': 0,
                'emoji_counter': Counter(),
                'sticker_usage': 0,
                'sticker_counter': Counter(),
            },
            'words_counter': Counter(),
        }


# Dictionary containing everything about the chat
messenger_chat = {
    'total_messages': 0,
    'word_count': 0,
    'character_count': 0,
    'image_count': 0,
    'gif_count': 0,
    'video_count': 0,
    'audio_count': 0,
    'link_count': 0,
    'reaction_count': {
        'given': 0,
        'reaction_counter': Counter(),
    },
    'other': {
        'like_usage': 0,
        'emoji_usage': 0,
        'emoji_counter': Counter(),
        'sticker_usage': 0,
        'sticker_counter': Counter(),
    },
    'words_counter': Counter(),
    'members': {},
}

# Runs the file
main(messenger_chat)
