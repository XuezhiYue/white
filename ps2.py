#!/Users/wxl/anaconda3/bin/python3.7
# coding=gbk

"""
  @Author  : Yxz
  @contact: yuexuezhi091@gmail.com
  @Software: PyCharm
  @FileName: test.py
  @Time    : 2020/5/27 14:36
  @desc:
"""

import datetime
import os
import re

def usage():
    print("Usage:")
    print("")
    print("photoscan.sh -platform offscreen -r process.py <path to project folder>")
    print("")
    print("photoscan.sh is the main Agisoft PhotoScan executable")
    print("If you remove -platform offscreen, the application will run with GUI")
    print("Project folder should containt the folder 'photos' with DNG or JPG files inside")
    exit()

try:
    import PhotoScan
except:
    print("Cannot import module PhotoScan")
    print("You shouldn't run this script by python interpreter. Use Agisoft PhotoScan instead.")
    usage()

# project log
def log(txt_path):
    path = txt_path + "\\" + "log.txt"
    print(path)
    logfile = open(path, "a")

    return logfile

txt_path = r"D:\uav_out"

logfile = log(txt_path)

def logAction(text):

    logfile.write("{} {}\n".format(datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S'), text))
    logfile.flush()

def image_name(image_folder):
    """get outimage name"""
    image_folder = image_folder
    image_name = image_folder.split("\\")[-1]
    return image_name

def getPhotoList(image_folder):
    """#get the photo list in specified folder"""
    photoList = []
    # 正则表达式获取dng/jgp
    print(image_folder)
    pattern = re.compile('(\.dng|\.jpg|\.tif)$', re.IGNORECASE)
    for root, dirs, files in os.walk(image_folder):
        for name in files:
            if pattern.search(name):
                cur_path = os.path.join(image_folder, name)
                photoList.append(cur_path)
    if len(photoList)<=0:

        print("No photo, cheack image folder{}".format(image_folder))
    else:
        print("photo nubmer{}".format(len(photoList)))

    return photoList

def progress(p):
    print("Progress: {0}".format(p))

def createOrOpenProject(root_path, image_folder):
    """creat a project by root_path and image_folder"""
    doc = PhotoScan.app.document
    name = image_name(image_folder)
    psxfile = root_path + "\\" + name + '.psx'

    if os.path.isfile(psxfile):
        doc.open(psxfile)
        logAction('Opened: ' + psxfile)
    else:
        doc.save(psxfile)
        logAction('New project saved to: ' + psxfile)

    return doc

def saveProject(doc):
    t = datetime.datetime.now()
    doc.save()
    logAction("Saved the project ({})".format(datetime.datetime.now() - t))

def addPhotos(chunk, image_folder):

    PhotoList = getPhotoList(image_folder)
    print("start add photo")
    chunk.addPhotos(PhotoList)

def alignPhotos(chunk):
    ## Perform image matching for the chunk frame.
    # matchPhotos(accuracy=HighAccuracy, preselection=NoPreselection, filter_mask=False, keypoint_limit=40000, tiepoint_limit=4000[, progress])
    # - Alignment accuracy in [HighestAccuracy, HighAccuracy, MediumAccuracy, LowAccuracy, LowestAccuracy]
    # - Image pair preselection in [ReferencePreselection, GenericPreselection, NoPreselection]
    # chunk.matchPhotos(
    #     accuracy=PhotoScan.HighestAccuracy,
    #     preselection=PhotoScan.ReferencePreselection,
    #     filter_mask=False,
    #     keypoint_limit=40000,
    #     tiepoint_limit=0,
    #     progress=progress)
    chunk.matchPhotos(
        accuracy=PhotoScan.HighestAccuracy,
        preselection=PhotoScan.ReferencePreselection,
        filter_mask=False,
        keypoint_limit=40000,
        tiepoint_limit=0)

    chunk.alignCameras()


def buildDenseCloud(chunk):
    ## Generate depth maps for the chunk.
    # buildDenseCloud(quality=MediumQuality, filter=AggressiveFiltering[, cameras], keep_depth=False, reuse_depth=False[, progress])
    # - Dense point cloud quality in [UltraQuality, HighQuality, MediumQuality, LowQuality, LowestQuality]
    # - Depth filtering mode in [AggressiveFiltering, ModerateFiltering, MildFiltering, NoFiltering]
    # chunk.buildDenseCloud(
    #     quality=PhotoScan.HighQuality,
    #     filter=PhotoScan.ModerateFiltering,
    #     progress=progress)
    chunk.buildDenseCloud(
        quality=PhotoScan.MediumQuality,
        filter=PhotoScan.ModerateFiltering,
    )

def buildsource(chunk):
    chunk.buildModel(
        surface=PhotoScan.SurfaceType.Arbitrary,
        source=PhotoScan.PointsSource.DensePoints,
        interpolation=PhotoScan.Interpolation.EnabledInterpolation,
        face_count=face_num)

def buildtexture(chunk):
    chunk.buildUV(mapping=PhotoScan.MappingMode.GenericMapping, count=1)
    chunk.buildTexture(blending=PhotoScan.BlendingMode.MosaicBlending, color_correction=False, size=8192)

def buildDEM(chunk):
    ### build DEM (before build dem, you need to save the project into psx) ###
    ## Build elevation model for the chunk.
    # buildDem(source=DenseCloudData, interpolation=EnabledInterpolation[, projection ][, region ][, classes][, progress])
    # - Data source in [PointCloudData, DenseCloudData, ModelData, ElevationData]
    # chunk.buildDem(
    #     source=PhotoScan.DenseCloudData,
    #     interpolation=PhotoScan.EnabledInterpolation,
    #     projection=chunk.crs,
    #     progress=progress)
    chunk.buildDem(
        source=PhotoScan.DenseCloudData,
        interpolation=PhotoScan.EnabledInterpolation,
        projection=chunk.crs,
    )


def buildOrtho(chunk):
    ## Build orthomosaic for the chunk.
    # buildOrthomosaic(surface=ElevationData, blending=MosaicBlending, color_correction=False[, projection ][, region ][, dx ][, dy ][, progress])
    # - Data source in [PointCloudData, DenseCloudData, ModelData, ElevationData]
    # - Blending mode in [AverageBlending, MosaicBlending, MinBlending, MaxBlending, DisabledBlending]
    chunk.buildOrthomosaic(
        surface=PhotoScan.ElevationData,
        blending=PhotoScan.DisabledBlending,
        color_correction=True,
        projection=chunk.crs,
    )

def exportDem(chunk, root_path):
    chunk.exportDem(
        root_path + '/dem.tif')


def exportOrtho(chunk, root_path, out_image_name):
    chunk.exportOrthomosaic(root_path + out_image_name+".tif")


def main(root_path, image_folder):

    # PhotoScan.app.messageBox('hello world! \n')
    # PhotoScan.app.console.clear()
    # PhotoScan.app.gpu_mask = 1

    """1: creat project"""
    doc = createOrOpenProject(root_path, image_folder)

    """2: creat chunk"""
    chunk = PhotoScan.Chunk

    if len(doc.chunks) > 0:
        chunk = doc.chunk
        logAction("Using the existing chunk '{}'".format(chunk.label))
    else:
        chunk = doc.addChunk()
        chunk.crs = PhotoScan.CoordinateSystem("EPSG::4326")
        logAction("Created the new chunk '{}'".format(chunk.label))

    if len(chunk.cameras) > 0:
        logAction("Skipping adding photos and aligning cameras because chunk already has {} cameras".format(
            len(chunk.cameras)))
    else:
        logAction("Started adding photos")
        t = datetime.datetime.now()
        addPhotos(chunk, image_folder)
        logAction("Added photos ({})".format(datetime.datetime.now() - t))

        logAction("Started photos alignment")
        t = datetime.datetime.now()

        """3: alignPhotos"""
        alignPhotos(chunk)
        logAction("Aligned photos ({})".format(datetime.datetime.now() - t))
        saveProject(doc)

    """4:Create point cloud"""
    if chunk.dense_cloud is None:
        logAction("Started buildling dense cloud")
        t = datetime.datetime.now()
        buildDenseCloud(chunk)
        logAction("Built dense cloud ({})".format(datetime.datetime.now() - t))
        saveProject(doc)
    else:
        logAction("Skipping dense cloud build because chunk already has {}".format(chunk.dense_cloud))

    """5:buildsource"""
    logAction("Started buildling source")
    t = datetime.datetime.now()
    buildsource(chunk)
    logAction("Built source ({})".format(datetime.datetime.now() - t))
    saveProject(doc)

    """6: buildtexture"""
    logAction("Started buildling texture")
    t = datetime.datetime.now()
    buildtexture(chunk)
    logAction("Built texture ({})".format(datetime.datetime.now() - t))
    saveProject(doc)

    """7: buildorthomosaic"""
    logAction("Started buildling orthomosaic")
    t = datetime.datetime.now()
    buildOrtho(chunk)
    logAction("Built orthomosaic ({})".format(datetime.datetime.now() - t))
    saveProject(doc)

    """8: exporting orthomosaic"""
    logAction("Started exporting orthomosaic")
    t = datetime.datetime.now()
    out_image_name = image_name(image_folder)
    exportOrtho(chunk, root_path, out_image_name)
    logAction("Exported orthomosaic ({})".format(datetime.datetime.now() - t))

if __name__ == '__main__':

    out_path = r"D:\uav_out"

    path = r"\\192.168.0.234\nydsj\烟草项目2020"

    PS = []

    for root, dirs, files in os.walk(path):

        for dir in dirs:
            new_path = path + "\\" + dir

            PS.append(new_path)

    log(out_path)

    for image_folder in PS:


        project = out_path + "\\" + image_name(image_folder)

        os.mkdir(project)


        main(project, image_folder)
