import bdata.porn.xvideos as xv
from blib.list_file_io import read_strlist, write_strlist
from blib.list_operation import list_unique, list_difference


def main():
    Downloaded = try_read_file("Downed.txt")

    URLs = list_difference(Downloaded, list_unique(read_strlist("ToDown.txt")))

    print "Finally get %d URLs in file." % len(URLs)
    xv.auto_process_urls(
        URLs,
        "D:/HTTP_DIR/src/get/xvideos/"
    )

    Downloaded += URLs

    write_strlist("Downed.txt", list_unique(Downloaded))


def try_read_file(filename):
    try:
        return read_strlist(filename)
    except:
        return []


if __name__ == "__main__":
    main()
