import os
import piexif
import shutil
import logging
import time

folder_list = []
image_list = []
accepted_ext = [
    ".JPG",
    ".JPEG",
    ".MP4",
    ".MOD",
    ".PNG",
    ".TIFF",
    ".MOV",
    ".WAV",
    ".AVI",
    ".MKV",
    ".GIF",
    ".BMP"
]
drive_path = ""

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
DRIVE_DIR = ""
EXIF = ""

logging.basicConfig(
    filename=os.path.join(CURRENT_DIR, "info.log"), filemode="w", level=logging.INFO
)
logger = logging.getLogger()


def create_folders():
    global folder_list
    folder_list = []

    for date in image_list:
        folder_list.append(date[1])
    folder_list = set(folder_list)

    for date in folder_list:
        date = str(date).replace(":", "-")
        if not os.path.isdir(os.path.join(DRIVE_DIR, date)):
            os.mkdir(os.path.join(DRIVE_DIR, "{}".format(date)))
            logger.info("The folder for {} was created".format(date))
        else:
            logger.info("The folder for {} is already created".format(date))
            continue


def read_images(drive_path):
    global image_list, unknown_list
    num_read, num_files, num_invalid, num_mod = 0, 0, 0, 0
    for root, dirs, files in os.walk(drive_path):
        # print(dirs)
        for name in files:
            filepath = os.path.join(root, name)
            __, extension = os.path.splitext(filepath)

            if "$RECYCLE.BIN" in filepath or "System Volume Information" in filepath:
                continue
            elif extension.upper() not in accepted_ext:
                num_files += 1
                num_invalid += 1
                continue
            elif name.startswith('.'):
                num_invalid += 1
                logger.warn("HIDDEN FILE {} FOUND".format(name))
                continue

            num_files += 1
            try:
                EXIF = piexif.load(filepath)
                date = EXIF["Exif"][piexif.ExifIFD.DateTimeOriginal]
                new_date = date.decode("utf-8")[0:7]
                new_date = str(new_date).replace(":", "-")
                image_list.append([filepath, new_date, root])
                logger.info(" Read {}".format(name))
                print(filepath, new_date)
                num_read += 1

            except Exception:
                mod_time = os.path.getmtime(filepath)
                time_mod = time.ctime(mod_time)
                obj = time.strptime(time_mod)
                time_stamp = time.strftime("%Y-%m", obj)
                image_list.append([filepath, "{}".format(time_stamp), root])
                logger.error(
                    "{} did not load date taken, but loaded mod date".format(name)
                )
                num_mod += 1
                continue

    logger.info("Total Amount of files: {}".format(num_files))
    logger.info("Total Amount of date taken files read: {}".format(num_read))
    logger.info(
        "Total Amount of files mod date files read: {}".format(num_mod)
    )
    logger.info("Total Amount of invalid files: {}\n\n".format(num_invalid))


def move_images():
    global image_list
    num_moved = 0

    for date in image_list:
        print(date[0], os.path.join(DRIVE_DIR, date[1] + os.sep + os.path.basename(date[2]) + os.sep + os.path.basename(date[0])))
        #print(os.path.join(DRIVE_DIR, date[1] + os.sep + os.path.basename(date[0])))
        
        #print(date[0],
        #    os.path.join(DRIVE_DIR, date[1] + os.sep + os.path.basename(date[2])))
        ## throw a try catch for whether the file is the same
        # os.replace(date[0], os.path.join(DRIVE_DIR, date[1] + os.sep + os.path.basename(date[0])))
        
        if date[2] == DRIVE_DIR.lower():
            shutil.copy2(date[0], os.path.join(DRIVE_DIR, date[1] + os.sep + os.path.basename(date[0])))
            num_moved += 1
            logger.info("Moved {}".format(os.path.basename(date[0])))
            #################
            # check to see if the file exists and then note whether it downloaded correctly i.e. compare teh new destination with the old source location
            #################
        else:
            folder_path = os.path.join(DRIVE_DIR, date[1] + os.sep + os.path.basename(date[2]))
            if not os.path.isdir(folder_path):
                os.mkdir(os.path.join(DRIVE_DIR, date[1] + os.sep + os.path.basename(date[2])))
            shutil.copy2(date[0], os.path.join(DRIVE_DIR, date[1] + os.sep + os.path.basename(date[2]) + os.sep + os.path.basename(date[0])))
            logger.info("Moved {}".format(os.path.basename(date[0])))
            num_moved += 1
        
            #logger.error("FILE {} WAS NOT MOVED OVER".format(os.path.basename(date[0])))
    logger.info("Total Amount of files moved {}".format(num_moved))


if __name__ == "__main__":
    print("What is the path of the drive you want?")
    drive_path = input() + os.sep
    DRIVE_DIR = os.path.dirname(os.path.realpath(drive_path))

    print(DRIVE_DIR)
    if not os.path.ismount(drive_path):
        print("That is not a correct drive location, retry\n")
        exit()
    else:
        print("This is a valid drive location\n")

    read_images(drive_path)
    create_folders()
    move_images()

    ######
    ## __, extension = os.path.splitext(filepath)
    ## image_list.append([filepath, "{}".format(extension)])
