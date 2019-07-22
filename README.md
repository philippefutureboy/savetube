# savetube

_For all those that want to ensure the perennity of their youtube videos_

`savetube` allows you to extract data from youtube's metadata and to apply it to `.mp3` and `.m4a` files
using a powerful mix of regular expressions and [Handlebars.js templating](https://handlebarsjs.com/).

`savetube` works by watching folders for files that are renamed to the format `{YOUTUBE_VIDEO_ID}.(m4a|mp3)`.

`savetube` supports watching multiple directories with different configurations, and automatically discovers
any configuration files in the watched directories (and subdirectories if `--recursive` is set) upon launch.
This is great for simultaneously downloading different playlist with different formats and information.

`savetube` allows you to save all of the commonly used ID3 tags, including songname, artist, album, album_artist, compilation and more.

`savetube` has only been used on macOS 10.13.6 and may not work on Windows or Linux machine.

## Installation

1. Clone this repository in a directory of your choice.

```bash
$ git clone https://github.com/philippefutureboy/savetube
```

2. Install `youtube-dl`. See [this tutorial](https://github.com/ytdl-org/youtube-dl/blob/master/README.md#installation)

3. Install `pipenv`. See [this tutorial](https://hackernoon.com/reaching-python-development-nirvana-bb5692adf30c)

4. Install `Node.js` & `npm`. See [Node.js installation page](https://nodejs.org/en/download/)

5. `cd` into the repository's directory. Install the project's dependencies:

```bash
$ cd savetube
$ npm i
$ pipenv install
```

6. Start using it!

## CLI Usage

```bash
$ pipenv run start --help
savetube: apply your youtube metadata to id3 tags

optional arguments:
  -h, --help            show this help message and exit
  --dry youtube_video_id savetuberc_path
                        Prints the raw data as well as the render_data that is
                        available to you once parsed. Incompatible with the
                        --watch and --out flags.
  --dry_out src_root src_filename out_template
                        Dry-run the out_template given the src_root and
                        src_filename provided. Must be used jointly with --dry
  --watch dir [dir ...]
                        Directories to watch. Supports multiple independent
                        directories by specifying them after the --watch flag.
                        The number of watch directories must match the number
                        of out directory templates
  --recursive           Specifies if watched directories should be recursively
                        watched.
  --out out_template [out_template ...]
                        Template path for the destination filename. Supports
                        multiple independent destinations by specifying them
                        after the --out flag. The number of out directory
                        templates must match the number of watch directories.
                        Non-existent directories will be created
```

### Examples

**Dry Run:**

The `--dry` and `--dry_out` flags will help you determine what information is available to you from the
`youtube-dl` metadata as well as from the filename configuration. The dry-run is useful to use to test
your configuration for proper output before doing a real run. 

```bash
$ pipenv run start \
  --dry L-gND6ro5zM "/Volumes/Some Volume/some_directory/some_subdirectory/savetuberc.json" \
  --dry_out "/Volumes/Some Volume/some_directory/" \
            "/Volumes/Some Volume/some_directory/some_subdirectory/L-gND6ro5zM.m4a" \
            "/Volumes/Some Volume/out/{{config.src_root_relative_dirname}}/{{tags.artist}} – {{tags.songname}}.{{config.src_extname}}"
```



**Normal Runs:**

The `--watch` flag allows you to specify one or more directories to watch for file changes. `savetube` concerns itself only with rename fs events as it assumes that your watch directory points to a directory in which you are downloading the files.

For each directory specified with the `--watch` flag, a out directory template string must be specified as an argument of the `--out` flag.

The `--recursive` flag signals to `savetube` to find `savetuberc.json` configuration files recursively from the specified root watch directories and to watch these subdirectories (and their children) and apply the local `savetuberc.json` config.

(Single directory)

```bash
$ pipenv run start \
  --watch "/Volumes/Some Volume/some_directory/" \
  --out "/Volumes/Some Volume/out/{{config.src_root_relative_dirname}}/{{tags.artist}} – {{tags.songname}}.{{config.src_extname}}" \
  --recursive
```

(Multiple directories)

```bash
$ pipenv run start \
  --watch "/Volumes/Some Volume/some_directory/" "/Volumes/Some Volume/another_directory/" \
  --out "/Volumes/Some Volume/some_out_dir/{{config.src_root_relative_dirname}}/{{tags.artist}} – {{tags.songname}}.{{config.src_extname}}" \
   "/Volumes/Some Volume/another_out_dir/{{config.src_root_relative_dirname}}/{{tags.artist}} – {{tags.songname}}.{{config.src_extname}}" \
  --recursive
```


If the rendered `--out` template strings point to an invalid path string (one that cannot be interpreted by the system), it will result in raised exception and failure to save the file. Hence make sure to dry run first and have some fallback properties in your templates, like so:

```sh
"/Volumes/Some Volume/another_out_dir/{{config.src_root_relative_dirname}}/{{#if tags.songname}}{{tags.songname}}{{else}}{{info.title}}{{/if}}.{{config.src_extname}}"
```

## `savetuberc.json`

The `savetuberc.json` file is where you will configure how to parse youtube-dl's information as well as 
what content you want to be written in the ID3 tags. It consists into 4 major parts:

1. `parsers`: Where you specify regular expressions to extract the information you are interested in
2. `config`: Where you specify any extra metadata that you want to be available for you when rendering
your tags
3. `tags`: Where you specify the Handlebars templates to form the values for your tags 
4. extra configuration flags

### `parsers`

**`parsers.title`**

Under `parsers.title`, you can parse the Youtube video's title. For instance, the songname and artist can be extracted from the video [madcat - Sunset (eGkfqt3C9aQ)](https://www.youtube.com/watch?v=eGkfqt3C9aQ)'s title using the following configuration:

```json
{
  "parsers": {
    "title": {
      "songname": "(?P<artist>.*)\\s+-\\s+(?P<songname>.*)",
      "artist": "(?P<artist>.*)\\s+-\\s+(?P<songname>.*)"
    },
  },
  ...
}
```

Where `parsers.title.songname` will look for the `<songname>` named group and extract it for later use, and similarly will do the same with `parsers.title.artist` and `<artist>` named group.

After this, you will end up with the following available configuration for your tags:

```json
{
  "info": {
    "title": "madcat - Sunset",
    ...
  },
  "title": {
    "songname": "Sunset",
    "artist": "madcat"
  },
  ...
}
```

For the complete list of available properties, go to the [Available Properties Section](#available_properties).

**`parsers.description`**

Just like `parsers.title`, the `parsers.description` section of the configuration file allows you to
specify regular expressions to extract meaningful data from the raw text. In the case of the previously mentioned video ([madcat - Sunset](https://www.youtube.com/watch?v=eGkfqt3C9aQ)), the description looks like this:

```
PREMIERE on Soundcloud: https://goo.gl/hbfDed

Label: FHUO Records
Artist: Madcat
Format: Vinyl
Cat Number: FHUO008
EP Title: Petite Musique de Chanvre
Release Date: June 2018

FHUO Records:
https://soundcloud.com/forheavenuseon...
https://www.facebook.com/forheavenuse...

madcat:
https://soundcloud.com/madcat_music
https://www.facebook.com/realmadcatmusic
---------------------------------------------------------------------------------------------------------------------------------------------------------------
Houseum:
https://soundcloud.com/houseum
https://www.facebook.com/houseum.yt
https://www.instagram.com/houseumrecords
```

From this wealth of information, we can extract the label, the artist, the format, the cat_number, and even more.
Here's a configuration that does just that:

```json
{
  "parsers": {
    "description": {
      "artist": "Artist:\\s+(?P<artist>.*)",
      "album": "EP Title:\\s+(?P<album>.*)",
      "label": "Label:\\s+(?P<label>.*)",
      "cat_number": "Cat Number:\\s+(?P<cat_number>.*)",
      "record_format": "Format:\\s+(?P<record_format>.*)",
      "release_year": "Release Date:\\s+.*(?P<release_date>.*(?P<release_year>\\d{4}))$"
    },
    ...
  },
  ...
}
```

For an output of:

```json
{
  "info": {
    "description": ...,
    ...
  },
  "description": {
    "artist": "Madcat",
    "album": "Petite Musique de Chanvre",
    "label": "FHUO Records",
    "cat_number": "FHUO008",
    "record_format": "Vinyl",
    "release_year": "2018",
  },
  ...
}
```

For Regular Expressions used in the `parsers.description` block, all matching lines are added together, separated by a UNIX/MacOS new line character, `\n`.
This can be useful for the `tracklist` field, which can be matched using something like the following:

```json
{
  "parsers": {
    "description": {
      ...,
      "tracklist": "(?P<tracklist>[0-9]+:[0-9]+\\s+.*)"
    },
    ...
  },
  ...
}
```


### `config`

The `config` property allows you to specify your own metadata to have them when
rendering your tags and your `--out` templates.
The file info is dumped in this `config` property before rendering the `--out`
templates. The file info you will find is the following:

Given the watch folder `/Volumes/Some Volume/some_directory/`,

Given a file of interest located at `/Volumes/Some Volume/some_directory/some_subdir/eGkfqt3C9aQ.m4a`,

```json
{
  "config": {
    "src_filename": "/Volumes/Some Volume/some_directory/some_subdir/eGkfqt3C9aQ.m4a",
    "src_dirname": "/Volumes/Some Volume/some_directory/some_subdir",
    "src_basename": "eGkfqt3C9aQ.m4a",
    "src_extname": "m4a",
    "src_root": "/Volumes/Some Volume/some_directory/",
    "src_root_relative_dirname": "some_subdir",
    ...
  },
  ...
}
```

### `tags`

`tags` are where you specify what information you want to be saved in your file's ID3 tags.
These are specified via Handlebars.js templates.
In your tags template, you can make reference to information found in the `info` obtained
from `youtube-dl`, in the parsed `title` block, in the parsed `description` block, or
in the `config` block.

As specified above, the file information will not be included at tag render time,
but only at `--out` template render time.

Here is an example of a tags configuration:

```json
{
  "tags": {
    "songname": "{{#if title.songname}}{{title.songname}}{{else}}{{info.title}}{{/if}}",
    "album": "{{#if description.album}}{{description.album}}{{else}}{{info.album}}{{/if}}",
    "artist": "{{#if title.artist}}{{title.artist}}{{else}}{{description.artist}}{{/if}}",
    "release_year": "{{#if description.release_year}}{{description.release_year}}{{else}}{{info.upload_year}}{{/if}}",
    "album_artist": "{{#if title.artist}}{{title.artist}}{{else}}{{description.artist}}{{/if}}",
    "composer": "{{#if info.uploader}}{{info.uploader}}{{else}}{{litteral:HATE}}{{/if}}",
    "comment": "{{info.description}}\n\nTracklist:\n{{description.tracklist}}",
    "tracklist": "{{description.tracklist}}"
  },
  ...
}
```

### Extra configuration flags

Since Apple Itunes truncates the comment tag at 250 characters, some extra measures have
to be taken to keep all of the info from your metadata intact.

**`save_tracklist_in_lyrics`**

Just as the properties means. Appends the tracklist to the lyrics tag, since lyrics
are unbounded. Defaults to `true`.

**`append_all_data_in_lyrics`**

Appends the equivalent of the result of `--dry` run to the lyrics as a stringified,
minified JSON string. Defaults to `true`.

**`save_all_data_on_file`** 

Saves the equivalent of the result of `--dry` run in the `savetube` custom tag.
Defaults to `true`.


## Available Properties

When parsing input from `youtube-dl`, these fields are supported by default:

```python
{
  "songname": str,
  "artist": str,
  "album": str,
  "album_artist": str,
  "compilation": str,
  "composer": str,
  "release_year": int,
  "comment": str,
  "tracklist": str,
  "disk_1": int,
  "disk_2": int,
  "trkn_1": int,
  "trkn_2": int
}
```

These are fields that match the commonly used ID3 tags on music files.
You can specify extra fields in both the `parsers` and in the `tags` sections of the configuration.
Keep in mind however that only the default properties seen above will be saved in the ID3 tags.
Hence you can parse your own fancy fields from the youtube-dl info, and refer them when building your
ID3 tag values, but you cannot add your own custom tags.

