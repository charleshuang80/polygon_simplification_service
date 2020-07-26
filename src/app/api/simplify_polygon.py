from fastapi import APIRouter, HTTPException, File, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse
import logging, tempfile, zipfile, os, geopandas, shutil, fiona

router = APIRouter()

# could not use ArcPy (for now) due to license issues
# @router.post("/shapefile/esri", tags=["shapefile"])
# # def shapefile_esri(file: UploadFile = File(...)):
# def shapefile_esri(file: bytes = File(...)):
#
#     with tempfile.TemporaryDirectory() as temp_dir:
#         print(temp_dir)
#         os.chdir(temp_dir)
#         os.mkdir('input')
#         os.mkdir('unzipped')
#
#         print(f"working in {os.getcwd()}")
#         with open("input/zip_file.zip", 'wb') as new_file:
#             new_file.write(file)
#         print(f"output of listdir for /input {os.listdir(temp_dir + '/input')}")
#         with zipfile.ZipFile("input/zip_file.zip") as zip_file:
#             print(f"files in zip: {zip_file.namelist()}")
#             zip_file.extractall('unzipped')
#             # unzipped_files = [f for f in os.listdir('unzipped')]
#         unzipped_files = os.listdir('unzipped')
#         # print(f"output of listdir for unzipped {os.listdir('unzipped')}")
#
#     return {"did it work?": unzipped_files}

# Geopandas Simplify uses Shapely
# https://geopandas.org/reference.html#geopandas.GeoSeries.simplify
# https://shapely.readthedocs.io/en/latest/manual.html#object.simplify

# TODO: may be able to specify some params, like tolerance, with additional Form params
# https://fastapi.tiangolo.com/tutorial/request-forms-and-files/


top_level_path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__))))

# background task to remove folders used to store output
def remove_output_folder(new_dir_name: str):
    # print("in remove folder background task")
    # print(new_dir_name)
    shutil.rmtree(new_dir_name)

# # https://fastapi.tiangolo.com/advanced/custom-response/
# using File response which requires async
@router.post("/shapefile/geopandas", tags=["shapefile"])
async def shapefile_geopandas(background_tasks: BackgroundTasks, file: bytes = File (...)):
    # for some reason the FastAPI/Starlette FileResponse cannot find the file
    # in the TemporaryDirectory, so we need to create a working dir
    # and remove it after
    working_dir_name = 'working'
    os.makedirs(os.path.join(top_level_path, working_dir_name), exist_ok=True)
    print("new folder exists? ", os.listdir(top_level_path))
    working_path = os.path.join(top_level_path, working_dir_name)

    background_tasks.add_task(remove_output_folder, working_path)

    os.chdir(working_path)
    # print("now working in: ", os.getcwd())
    os.mkdir('input')
    os.mkdir('processing')
    os.mkdir('output')

    with open("input/zip_file.zip", 'wb') as new_file:
        new_file.write(file)

    simplification_count = 0
    # because the zipfile is binary zipped shapefile, Fiona would require us
    # to use ZipMemoryFile (https://fiona.readthedocs.io/en/latest/manual.html#memoryfile-and-zipmemoryfile), which requires knowing the name of the shapefile
    # with ZipMemoryFile(data) as zip:
    os.mkdir("processing/" + str(simplification_count))
    with zipfile.ZipFile("input/zip_file.zip") as zip_file:
        zip_file.extractall("processing/" + str(simplification_count))

    # 1. open simplified file w/ fiona
    # 2. run point count
    # 3. if it is too high:
        # opt A
            # a. read file w/ gp
            # b. simplify
            # c. rmtree processed
            # d. mkdir processed
            # e. to_file in processed
            # f. open file w/ fiona and run point count
        # opt B
            # a. increment processing count
            # b. mkdir with processing count
            # c. read previous processed file, simplify, to file in new dir
            # d. open new shp w/ fiona and run point count
    simp_tolerance = 0.2 # want to increment this?
    need_to_simplify = True
    while need_to_simplify: #  and simplification_count < 10  # may need to prevent infinite loops while testing
        old_processing_path = "processing/" + str(simplification_count)
        # print(f"simplification process #{simplification_count + 1}, from {old_processing_path}")
        shp_file = [f for f in os.listdir(old_processing_path) if f.endswith('.shp')][0]
        df = geopandas.read_file(os.path.join(old_processing_path, shp_file))
        simplified_gs = df.simplify(simp_tolerance) # preserve_topology = True by default

        new_processing_path = "processing/" + str(simplification_count + 1)
        os.mkdir(new_processing_path)
        # print("added new folder to work in: ", os.listdir("processing"))
        simplified_gs.to_file(os.path.join(new_processing_path, "simplified.shp"))
        # print("added new simplified shp in new folder: ", os.listdir(new_processing_path))
        simplified_shp = [f for f in os.listdir(new_processing_path) if f.endswith('.shp')][0]

        # geopandas did not expose fiona functionality that allowed us to count
        # the number of points, so we had to use fiona directly
        # this link was extremely helpful: https://gis.stackexchange.com/questions/119453/count-the-number-of-points-in-a-multipolygon-in-shapely
        num_features = 0
        num_points = 0
        with fiona.open(os.path.join(new_processing_path, simplified_shp)) as fs_file:
            # can simplify reduce the # of features? probably not...
            num_features = len(fs_file)
            print("num features: ", num_features)
            # number of features limit from CMR is 500
            for feature in fs_file:
                if feature['geometry']['type'] == 'Polygon':
                    if len(feature['geometry']['coordinates']) == 1:
                        # print("num points in simple poly: ", len(feature['geometry']['coordinates'][0]))
                        num_points += len(feature['geometry']['coordinates'][0])
                    elif len(feature['geometry']['coordinates']) > 1:
                        for part in feature['geometry']['coordinates']:
                            # polygon with holes
                            # print("num points in poly w/ hole: ", len(part))
                            num_points += len(part)
                if feature['geometry']['type'] == 'MultiPolygon':
                    # print("num points = ", sum([len(poly[0]) for poly in feature['geometry']['coordinates']]))
                    num_points += sum([len(poly[0]) for poly in feature['geometry']['coordinates']])

        print("total num_points: ", num_points)
        # 5000 is the limit for CMR
        if num_points <= 5000: need_to_simplify = False
        simplification_count += 1
        simp_tolerance += 0.1
        # print(f"end of loop. need_to_simplify: {need_to_simplify}; simp count: {simplification_count}; simp_tolerance: {simp_tolerance}")

    # make zip file
    archive_name = "output/simplified_polygon"
    shutil.make_archive(archive_name, "zip", new_processing_path)
    # print(f"file there? {os.listdir('output')}")

    full_path = os.path.abspath("output/simplified_polygon.zip")
    # print("path is", full_path)
    # print("is zip file?", zipfile.is_zipfile(full_path))
    # with zipfile.ZipFile(full_path) as zipped:
    #     print("in zipped: ", zipped.namelist())

    return FileResponse(full_path)



@router.post("/geojson/", tags=["shapefile"])
def accept_geojson(file: UploadFile = File(...)):
    print(f"file: {file}")
    root.info("file: {file}")
    return {"did it work?": root.info("file: {file}")}



# route for testing how to use geopandas to work with spatial data
@router.post("/shapefile/geopandas/testing", tags=["shapefile"])
def shapefile_geopandas_testing(file: bytes = File (...)):
    with tempfile.TemporaryDirectory() as temp_dir:
        os.chdir(temp_dir)
        os.mkdir('input')
        os.mkdir('unzipped')
        os.mkdir('processed')
        os.mkdir('output')

        with open("input/zip_file.zip", 'wb') as new_file:
            new_file.write(file)
        # because the zipfile is binary zipped shapefile, Fiona would require us
        # to use ZipMemoryFile (https://fiona.readthedocs.io/en/latest/manual.html#memoryfile-and-zipmemoryfile), which requires knowing the name of the shapefile
        # with ZipMemoryFile(data) as zip:
        with zipfile.ZipFile("input/zip_file.zip") as zip_file:
            zip_file.extractall('unzipped')
        shp_file = [f for f in os.listdir('unzipped') if '.shp' in f][0]
        df = geopandas.read_file("unzipped/" + shp_file)

        simplified_gs = df.simplify(0.2)
        # can fiona read the simplified gs?
        f = fiona.open(simplified_gs)
        print("fiona? ", f)

        # print(f"input projection = {df.crs}")
        # print("df.geometry: \n", df.geometry)
        # print("df.geom_type: \n", df.geom_type)
        # print("df.geometry[0]: \n", df.geometry[0])
        # print("df.geometry[0].geom_type: ", df.geometry[0].geom_type)
        # print("len(df.geometry[0]): \n", len(df.geometry[0]))
        # # print("df.geometry['geom_type']: \n", df.geometry['geom_type'])
        # print("df.geometry.keys(): \n", df.geometry.keys())
        # print("vars(df.geometry[0]).keys(): \n", vars(df.geometry[0]).keys())

        # shape = fiona.open("unzipped/" + shp_file)
        # geom = shape.next()['geometry']['coordinates']

        # geopandas did not expose fiona functionality that allowed us to count
        # the number of points, so we had to use fiona directly
        # this link was extremely helpful: https://gis.stackexchange.com/questions/119453/count-the-number-of-points-in-a-multipolygon-in-shapely
        num_features = 0
        num_points = 0
        with fiona.open("unzipped/" + shp_file) as fs_file:
            # can simplify reduce the # of features? probably not...
            num_features = len(fs_file)
            print("num features: ", num_features)
            for feature in fs_file:
                if feature['geometry']['type'] == 'Polygon':
                    if len(feature['geometry']['coordinates']) == 1:
                        print("num points in simple poly: ", len(feature['geometry']['coordinates'][0]))
                        num_points += len(feature['geometry']['coordinates'][0])
                    elif len(feature['geometry']['coordinates']) > 1:
                        for part in feature['geometry']['coordinates']:
                            # polygon with holes
                            print("num points in poly w/ hole: ", len(part))
                            num_points += len(part)
                if feature['geometry']['type'] == 'MultiPolygon':
                    print("num points = ", sum([len(poly[0]) for poly in feature['geometry']['coordinates']]))
                    num_points += sum([len(poly[0]) for poly in feature['geometry']['coordinates']])

            print("total number of points: ", num_points)

        return {"working on num_points": num_points, "num_features": num_features}
