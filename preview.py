import os
from juptex.notebook import isnotebook, Image


def genpdf(content, bib_path=None, clean=True, postfix=""):
  if not os.path.isdir("./view"):
    os.mkdir("view")
  if clean:
    ret = os.system(f"cd view && rm -rf view*")
    if ret != 0:
      print(f"Exit with error: {ret}")
      return False
  with open(f"./view/view{postfix}.tex", "w") as f:
    f.write(content)
  if bib_path:
    ret = os.system(f"cp {bib_path} ./view")
    if ret != 0:
      print(f"Exit with error: {ret}")
      return False
    ret = os.system("cd view && latexmk -pdf -halt-on-error -silent "
                    "> /dev/null 2> error.log")
  else:
    ret = os.system(f"cd view && pdflatex view{postfix}.tex "
                    "-halt-on-error -silent "
                    "> /dev/null 2> error.log")
  if ret != 0:
    print(f"Exit with error: {ret}")
    return False

  return True


def genpng(content, crop=True):
  if not genpdf(content):
    raise Exception("Failed to generate pdf")

  if crop:
    ret = os.system("pdfcrop ./view/view.pdf ./view/view-crop.pdf "
                    "1> /dev/null 2> /dev/null")
    if ret != 0:
      raise Exception(f"pdfcrop exit with error: {ret}")

    ret = os.system(
        "convert -density 600 ./view/view-crop.pdf "
        "./view/view.png 2> /dev/null")
    if ret != 0:
      raise Exception(f"Convert exit with error: {ret}")
  else:
    ret = os.system(
        "convert -density 600 ./view/view.pdf ./view/view.png 2> /dev/null")
    if ret != 0:
      raise Exception(f"Convert exit with error: {ret}")

  if isnotebook():
    return Image("./view/view.png")
  else:
    os.system("open ./view/view.png")
