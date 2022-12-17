import os


# Global configurations
root_path = os.path.join(os.getenv("HOME"), ".juptex")
essay_path = os.path.join(os.getenv("HOME"), "Documents/Essays")
slide_path = os.path.join(os.getenv("HOME"), "Documents/Slides")

# Matheq configurations
python_mark = "!"
instruction_mark = "%%",
line_splitter = "@"
space_holder = "~"
math_indent = 2

# Text parser configurations
python_start_mark, python_end_mark = "`", "`"
blockmath_start_mark, blockmath_end_mark = "$$", "$$"
math_start_mark, math_end_mark = "$", "$"
bold_start_mark, bold_end_mark = "**", "**"
emph_start_mark, emph_end_mark = "_", "_"
underline_start_mark, underline_end_mark = "<u>", "</u>"
cite_start_mark, cite_end_mark = "[[", "]]"
raw_start_mark, raw_end_mark = "<raw>", "</raw>"
pre_start_mark, pre_end_mark = "<code>", "</code>"
hide_start_mark, hide_end_mark = "<span hidden>", "</span>"
space_placeholder = "<space>"
bib_path = os.path.join(root_path, "reference.bib")

# Reference
reference_entry_black_list = [
    "file", "abstract"
]
