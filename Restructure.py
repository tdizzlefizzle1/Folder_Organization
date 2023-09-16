import os
import piexif
import shutil
import logging
import time
import filecmp

folder_list = []
image_list = []
dupes = []
counts = {}
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
    ".NEF",
    ".GIF",
    ".BMP",
    ".ARW",
    ".RAF",
    ".RAW",
]
drive_path = ""
num_moved, num_fail = 0, 0

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
DRIVE_DIR = ""
EXIF = ""

logging.basicConfig(
    filename=os.path.join(CURRENT_DIR, "info.log"), filemode="w", level=logging.INFO
)
logger = logging.getLogger()


def create_folders():
    global folder_list

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
    global image_list, unknown_list, dupes
    num_read, num_files, num_invalid, num_mod = 0, 0, 0, 0

    for root, dirs, files in os.walk(drive_path):
        print(root)
       #try:
       #    #spaced = os.path.
       #    #rep_name = root.replace(" ", "-")
       #    #print("root: ", rep_name)
       #    #os.replace(root, rep_name)

       #except PermissionError:
       #    print("warn")
       #    #print(root)
        for name in files:
            filepath = os.path.join(root, name)
            __, extension = os.path.splitext(filepath)
            dupes.append(name)

            if name.find(" "):
                rep_name = name.replace(" ", "-")
                os.replace(filepath, os.path.join(root, rep_name))
                filepath = os.path.join(root, rep_name)

            if "$RECYCLE.BIN" in filepath or "System Volume Information" in filepath:
                num_files += 1
                num_invalid += 1
                continue

            elif extension.upper() not in accepted_ext:
                num_files += 1
                num_invalid += 1
                continue
               
            elif name.startswith('.'):
                num_files += 1
                num_invalid += 1
                logger.warning("HIDDEN FILE {} FOUND".format(name))
                continue


            try:
                EXIF = piexif.load(filepath)
                date = EXIF["Exif"][piexif.ExifIFD.DateTimeOriginal]
                new_date = date.decode("utf-8")[0:7]
                new_date = str(new_date).replace(":", "-")
                image_list.append([filepath, new_date, root])
                logger.info(" Read {}".format(name))
                print(filepath, new_date)
                num_read += 1
                num_files += 1

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
                num_files += 1
                continue

    logger.info("Total Amount of files: {}".format(num_files))
    logger.info("Total Amount of date taken files read: {}".format(num_read))
    logger.info(
        "Total Amount of files mod date files read: {}".format(num_mod)
    )
    logger.info("Total Amount of invalid files: {}\n\n".format(num_invalid))


def check_duplicates():
    for name in image_list:
        print(name[0])
    

def move_images():
    global image_list

    for date in image_list:
        source_loc = date[0]
        folder_path = os.path.join(DRIVE_DIR, date[1] + os.sep + os.path.basename(date[2]))
        valid_loc = None
        print(date[0], os.path.join(DRIVE_DIR, date[1] + os.sep + os.path.basename(date[2]) + os.sep + os.path.basename(date[0])))
        #print(os.path.join(DRIVE_DIR, date[1] + os.sep + os.path.basename(date[0])))
        
        #print(date[0],
        #    os.path.join(DRIVE_DIR, date[1] + os.sep + os.path.basename(date[2])))
        ## throw a try catch for whether the file is the same
        # os.replace(date[0], os.path.join(DRIVE_DIR, date[1] + os.sep + os.path.basename(date[0])))
        while (valid_loc != True):
            if date[2] == DRIVE_DIR.lower():
                dest_loc = os.path.join(DRIVE_DIR, date[1] + os.sep + os.path.basename(date[0]))

                if os.path.isfile(dest_loc):
                    dest_loc = rename_files(dest_loc)
                    print("this is the dest", dest_loc)
                    
                shutil.copy2(source_loc, dest_loc)
                valid_loc = check_location(source_loc, dest_loc)

                #################
                # check to see if the file exists and then note whether it downloaded correctly i.e. compare teh new destination with the old source location
                #################
            else:
                dest_loc = os.path.join(DRIVE_DIR, date[1] + os.sep + os.path.basename(date[2]) + os.sep + os.path.basename(date[0]))

                if not os.path.isdir(folder_path):
                    os.mkdir(folder_path)

                if os.path.isfile(dest_loc):
                    dest_loc = rename_files(dest_loc)
                    print("this is the dest", dest_loc)
                
                shutil.copy2(date[0], dest_loc)
                valid_loc = check_location(source_loc, dest_loc)

    logger.info("Total Amount of files moved {}".format(num_moved))
    logger.info("Total Amount of failed attempts to move {}".format(num_fail))

def rename_files(dest):
    print("hello: ", dest)
    basename = os.path.basename(dest)
    name, extension = os.path.splitext(basename)

    if basename in counts: 
        counts[basename] += 1
        fixed_dest = "{}-{}{}".format(name, counts[basename], extension)
    else:
        counts[basename] = 1
        fixed_dest = "{}-{}{}".format(name, counts[basename], extension)

    
    #duplicates = [i for i in names if names.count(i) > 1] 
    logger.warning("{} is True so there is a duplicate".format("placeholder"))
    return os.path.join(os.path.dirname(dest), fixed_dest)


def check_location(src, dest):
    global num_moved, num_fail
    valid_loc = None

    try:
        valid_loc = filecmp.cmp(src, dest)
        num_moved += 1
        logger.info("Moved {}".format(os.path.basename(src)))

    except FileNotFoundError:
        valid_loc = False
        num_fail += 1
        logger.error("Failed to move {}".format(os.path.basename(src)))

    return valid_loc


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

    #check_duplicates()
    read_images(drive_path)
    #print(image_list)
    create_folders()
    move_images()
    print(counts)


    #print(check_location('F:\\100_FUJI\DSCF0251.JPG', 'F:\\2023-06\\100_FUJI\DSCF0251.JPG'))


    ######
    ## __, extension = os.path.splitext(filepath)
    ## image_list.append([filepath, "{}".format(extension)])
