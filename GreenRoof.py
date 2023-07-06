"""
Model exported as python.
Name : Mannheim._GreenRoofs_13
Group : projects
With QGIS : 32805
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterString
from qgis.core import QgsProcessingParameterField
from qgis.core import QgsProcessingParameterFile
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsExpression
import processing


class Mannheim_greenroofs_13(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('_building_footprint_shapefile', '1_Building footprint shapefile', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('_districts_shapefile', '2_Districts shapefile', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterVectorLayer('_solar_potential_shapefile', '3_Solar Potential shapefile', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterString('area_field_of_building_footprint_shapefile', 'Area field of building footprint shapefile', multiLine=False, defaultValue=''))
        self.addParameter(QgsProcessingParameterString('area_field_of_created_shapefile', 'Area Field of Created Shapefile ', multiLine=False, defaultValue=''))
        self.addParameter(QgsProcessingParameterField('area_field_of_solar_potential', 'Area Field of solar potential', type=QgsProcessingParameterField.Any, parentLayerParameterName='_solar_potential_shapefile', allowMultiple=False, defaultValue=None))
        self.addParameter(QgsProcessingParameterString('building_id_field_of_filtered_shapefile', 'Building ID Field of Filtered Shapefile ', multiLine=False, defaultValue=''))
        self.addParameter(QgsProcessingParameterField('building_id_of_solar_potential', 'Building ID of solar potential', type=QgsProcessingParameterField.Any, parentLayerParameterName='_solar_potential_shapefile', allowMultiple=False, defaultValue=None))
        self.addParameter(QgsProcessingParameterString('district_name_field', 'district name field', multiLine=False, defaultValue=''))
        self.addParameter(QgsProcessingParameterString('field_with_district_name', 'Field with District Name', multiLine=False, defaultValue=''))
        self.addParameter(QgsProcessingParameterFile('folder_to_save_created_shapefile', 'Folder to save created Shapefile', behavior=QgsProcessingParameterFile.Folder, fileFilter='All files (*.*)', defaultValue=None))
        self.addParameter(QgsProcessingParameterField('slope_field_of_solar_potential', 'Slope Field of solar potential', type=QgsProcessingParameterField.Any, parentLayerParameterName='_solar_potential_shapefile', allowMultiple=False, defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('PotentiallySuitableBuildings', 'Potentially Suitable Buildings', type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue='TEMPORARY_OUTPUT'))
        self.addParameter(QgsProcessingParameterFeatureSink('FinalDistrictShapefile', 'final district shapefile', optional=True, type=QgsProcessing.TypeVectorAnyGeometry, createByDefault=True, defaultValue='TEMPORARY_OUTPUT'))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(15, model_feedback)
        results = {}
        outputs = {}

        # Fix geometries for building footprint
        alg_params = {
            'INPUT': parameters['_building_footprint_shapefile'],
            'METHOD': 1,  # Structure
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixGeometriesForBuildingFootprint'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Fix geometries for district
        alg_params = {
            'INPUT': parameters['_districts_shapefile'],
            'METHOD': 1,  # Structure
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixGeometriesForDistrict'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Check validity for solar potential
        alg_params = {
            'IGNORE_RING_SELF_INTERSECTION': False,
            'INPUT_LAYER': parameters['_solar_potential_shapefile'],
            'METHOD': 2,  # GEOS
        }
        outputs['CheckValidityForSolarPotential'] = processing.run('qgis:checkvalidity', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Join attributes by location to add the Districts Name to the Footprints shapefile
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'INPUT': outputs['FixGeometriesForBuildingFootprint']['OUTPUT'],
            'JOIN': outputs['FixGeometriesForDistrict']['OUTPUT'],
            'JOIN_FIELDS': parameters['field_with_district_name'],
            'METHOD': 2,  # Take attributes of the feature with largest overlap only (one-to-one)
            'PREDICATE': [0],  # intersect
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByLocationToAddTheDistrictsNameToTheFootprintsShapefile'] = processing.run('native:joinattributesbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(4)
        if feedback.isCanceled():
            return {}

        # Conditional branch
        alg_params = {
        }
        outputs['ConditionalBranch'] = processing.run('native:condition', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(5)
        if feedback.isCanceled():
            return {}

        # Fix geometries
        alg_params = {
            'INPUT': parameters['_solar_potential_shapefile'],
            'METHOD': 1,  # Structure
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['FixGeometries'] = processing.run('native:fixgeometries', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(6)
        if feedback.isCanceled():
            return {}

        # Extract by expression (No Fix)
        alg_params = {
            'EXPRESSION': 'eval( @slope_field_of_solar_potential  )  <=  10 AND eval(  @area_field_of_solar_potential   )   >=   100\r\n',
            'INPUT': parameters['_solar_potential_shapefile'],
            'OUTPUT': QgsExpression(' @folder_to_save_created_shapefile ').evaluate(),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionNoFix'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(7)
        if feedback.isCanceled():
            return {}

        # Extract by expression (Fix)
        alg_params = {
            'EXPRESSION': 'eval( @slope_field_of_solar_potential  )  <=  10 AND eval(  @area_field_of_solar_potential   )   >=   100\r\n\r\n',
            'INPUT': outputs['FixGeometries']['OUTPUT'],
            'OUTPUT': QgsExpression(' @folder_to_save_created_shapefile ').evaluate(),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByExpressionFix'] = processing.run('native:extractbyexpression', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(8)
        if feedback.isCanceled():
            return {}

        # Statistics by categories to group by building ID
        alg_params = {
            'CATEGORIES_FIELD_NAME': parameters['building_id_field_of_filtered_shapefile'],
            'INPUT': QgsExpression(' @folder_to_save_created_shapefile ').evaluate(),
            'VALUES_FIELD_NAME': parameters['area_field_of_created_shapefile'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesToGroupByBuildingId'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(9)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value to join area of filtered with footprint shapefile
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': parameters['building_id_field_of_filtered_shapefile'],
            'FIELDS_TO_COPY': ['sum'],
            'FIELD_2': parameters['building_id_field_of_filtered_shapefile'],
            'INPUT': outputs['JoinAttributesByLocationToAddTheDistrictsNameToTheFootprintsShapefile']['OUTPUT'],
            'INPUT_2': outputs['StatisticsByCategoriesToGroupByBuildingId']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueToJoinAreaOfFilteredWithFootprintShapefile'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(10)
        if feedback.isCanceled():
            return {}

        # Extract by attribute to remove null values
        alg_params = {
            'FIELD': 'sum',
            'INPUT': outputs['JoinAttributesByFieldValueToJoinAreaOfFilteredWithFootprintShapefile']['OUTPUT'],
            'OPERATOR': 9,  # is not null
            'VALUE': '',
            'OUTPUT': parameters['PotentiallySuitableBuildings']
        }
        outputs['ExtractByAttributeToRemoveNullValues'] = processing.run('native:extractbyattribute', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['PotentiallySuitableBuildings'] = outputs['ExtractByAttributeToRemoveNullValues']['OUTPUT']

        feedback.setCurrentStep(11)
        if feedback.isCanceled():
            return {}

        # Statistics by categories final for area ST
        alg_params = {
            'CATEGORIES_FIELD_NAME': parameters['field_with_district_name'],
            'INPUT': outputs['ExtractByAttributeToRemoveNullValues']['OUTPUT'],
            'VALUES_FIELD_NAME': 'sum',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesFinalForAreaSt'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(12)
        if feedback.isCanceled():
            return {}

        # Statistics by categories final for area footprint
        alg_params = {
            'CATEGORIES_FIELD_NAME': parameters['field_with_district_name'],
            'INPUT': outputs['ExtractByAttributeToRemoveNullValues']['OUTPUT'],
            'VALUES_FIELD_NAME': parameters['area_field_of_building_footprint_shapefile'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['StatisticsByCategoriesFinalForAreaFootprint'] = processing.run('qgis:statisticsbycategories', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(13)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value final to join footprint and distrct shapefiles
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': parameters['field_with_district_name'],
            'FIELDS_TO_COPY': ['sum'],
            'FIELD_2': parameters['district_name_field'],
            'INPUT': outputs['FixGeometriesForDistrict']['OUTPUT'],
            'INPUT_2': outputs['StatisticsByCategoriesFinalForAreaFootprint']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': 'footprint_area',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['JoinAttributesByFieldValueFinalToJoinFootprintAndDistrctShapefiles'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(14)
        if feedback.isCanceled():
            return {}

        # Join attributes by field value final to join footprint and distrct shapefiles
        alg_params = {
            'DISCARD_NONMATCHING': False,
            'FIELD': parameters['district_name_field'],
            'FIELDS_TO_COPY': ['sum'],
            'FIELD_2': parameters['district_name_field'],
            'INPUT': outputs['JoinAttributesByFieldValueFinalToJoinFootprintAndDistrctShapefiles']['OUTPUT'],
            'INPUT_2': outputs['StatisticsByCategoriesFinalForAreaSt']['OUTPUT'],
            'METHOD': 1,  # Take attributes of the first matching feature only (one-to-one)
            'PREFIX': 'ST_area',
            'OUTPUT': parameters['FinalDistrictShapefile']
        }
        outputs['JoinAttributesByFieldValueFinalToJoinFootprintAndDistrctShapefiles'] = processing.run('native:joinattributestable', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['FinalDistrictShapefile'] = outputs['JoinAttributesByFieldValueFinalToJoinFootprintAndDistrctShapefiles']['OUTPUT']
        return results

    def name(self):
        return 'Mannheim._GreenRoofs_13'

    def displayName(self):
        return 'Mannheim._GreenRoofs_13'

    def group(self):
        return 'projects'

    def groupId(self):
        return 'projects'

    def createInstance(self):
        return Mannheim_greenroofs_13()
