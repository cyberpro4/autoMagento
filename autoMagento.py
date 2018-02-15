import argparse
import os
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser(description='Magento 1.9.x plugin generator.')

parser.add_argument('plugin', help="Name of the plugin. Ex: Mage", metavar='[PLUGIN]')

parser.add_argument('module', help="Name of the plugin module. Ex: Core or Sales", metavar='[MODULE]')

parser.add_argument('-c', '--collection', help="Name of the collection to generate (Models and Resources) Ex: Report")

parser.add_argument('-g', '--grid', help="Name of adminhtml grid to generate Ex: Report")

parser.add_argument('--version', help='Base version in case of non-existing plugin (default 0.1.0)', default='0.1.0')

parser.add_argument('--code', help='The code directory: core/local/community', default='local')

parser.add_argument('--base-path', help='Magento installation root (default is current directory)', default='.')

options = parser.parse_args()

if options.code not in ['local', 'core', 'community']:
    print 'Invalid code directory: must be "core" or "local" or "community"'
    exit(1)

appDir = '%s/app/' % options.base_path

if not os.path.exists(appDir):
    print 'Magento installation not found in %s' % appDir
    exit(1)

basePluginDir = '%s/code/%s/%s/%s/' % (appDir, options.code, options.plugin, options.module)

basePluginWithUnderscore = options.plugin + '_' + options.module
basePluginWithUnderscoreLowercase = options.plugin.lower() + '_' + options.module.lower()

configFile = basePluginDir + 'etc/config.xml'


def gen_dir(path):
    if os.path.exists(path):
        return
    os.makedirs(path)


def gen_file(path, default_content):
    if os.path.exists(path):
        return
    f = open(path, "w")
    f.write(default_content)
    f.close()


def gen_module():
    dirs = [
        basePluginDir + 'Block',
        basePluginDir + 'controllers',
        basePluginDir + 'etc',
        basePluginDir + 'Helper',
        basePluginDir + 'Model',
        basePluginDir + 'sql',
    ]

    for dir in dirs:
        if not os.path.exists(dir):
            os.makedirs(dir)

    # xml_file = './app/etc/modules/' + options.plugin + '_' + options.module + '.xml'
    xml_file = '%s/etc/modules/%s_%s.xml' % (appDir, options.plugin, options.module)

    if not os.path.exists(xml_file):
        xml = open(xml_file, "w")
        name = options.plugin + '_' + options.module
        xml.write("""<?xml version="1.0"?>
<config>
    <modules>
        <""" + name + """>
            <active>true</active>
            <codePool>local</codePool>
        </""" + name + """>
    </modules>
</config>""")


def gen_xml_path(file_path, path, content):
    print path

    if not os.path.exists(file_path):
        f = open(file_path, "w")
        f.write("""<?xml version="1.0"?>
<config>
    <modules>
        <%s_%s>
            <version>%s</version>
        </%s_%s>
    </modules>
</config>""" % (options.plugin, options.module, options.version, options.plugin, options.module))
        f.close()

    doc = ET.parse(file_path)
    node = doc.getroot()

    path = path.split('/')

    for path_part in path:
        if path_part == 'config':
            continue

        print path_part

        new_node = node.find(path_part)

        if new_node is None:
            new_node = ET.SubElement(node, path_part)

        node = new_node

    if content:
        node.text = content

    content = ET.tostring(doc.getroot(), encoding='utf8', method='xml')

    f = open(file_path, "w")
    f.write(content)
    f.close()


def gen_helper():

    gen_file(basePluginDir + 'Helper/Data.php', """<?php

class """ + basePluginWithUnderscore + """_Helper_Data extends Mage_Core_Helper_Abstract {
}""")

    gen_xml_path(configFile, 'config/global/helpers/' + basePluginWithUnderscoreLowercase + '/class',
                 basePluginWithUnderscore + '_Helper')


def gen_collection():
    if not options.collection:
        return

    gen_file("%s/Model/%s.php" % (basePluginDir, options.collection), """<?php

class %s_%s_Model_%s extends Mage_Core_Model_Abstract {

    public function __construct() {
        $this->_init('%s/%s' );
    }
}""" % (
        options.plugin, options.module, options.collection, basePluginWithUnderscoreLowercase,
        options.collection.lower()))

    gen_dir('%s/Model/Resource/%s' % (basePluginDir, options.collection))

    gen_file('%s/Model/Resource/%s.php' % (basePluginDir, options.collection), """<?php

class %s_%s_Model_Resource_%s extends Mage_Core_Model_Resource_Db_Abstract {

    public function _construct() {
        $this->_init('%s/%s', '%s_%s_id');
    }
}""" % (
        options.plugin, options.module, options.collection, basePluginWithUnderscoreLowercase,
        options.collection.lower(), basePluginWithUnderscoreLowercase, options.collection.lower()))

    gen_file('%s/Model/Resource/%s/Collection.php' % (basePluginDir, options.collection), """<?php

class %s_%s_Model_Resource_%s_Collection extends Mage_Core_Model_Resource_Db_Collection_Abstract {

    public function _construct() {
        parent::_construct();
        $this->_init('%s/%s');
    }
}""" % (
        options.plugin, options.module, options.collection, basePluginWithUnderscoreLowercase,
        options.collection.lower()))

    gen_xml_path(configFile, 'config/global/models/%s/class' % (basePluginWithUnderscoreLowercase),
                 basePluginWithUnderscore + '_Model')
    gen_xml_path(configFile, 'config/global/models/%s/resourceModel' % (basePluginWithUnderscoreLowercase),
                 basePluginWithUnderscoreLowercase + '_resource')

    gen_xml_path(configFile, 'config/global/models/%s/class' % (basePluginWithUnderscoreLowercase + '_resource'),
                 basePluginWithUnderscore + '_Model_Resource')

    table_name = basePluginWithUnderscoreLowercase + '_' + options.collection.lower()

    gen_xml_path(configFile, 'config/global/models/%s/entities/%s/table' % (
        basePluginWithUnderscoreLowercase + '_resource', options.collection.lower()), table_name)

    gen_dir('%s/sql/%s_setup/' % (basePluginDir, basePluginWithUnderscoreLowercase))

    gen_xml_path(configFile, 'config/global/resources/%s_setup/setup/module' % basePluginWithUnderscoreLowercase,
                 basePluginWithUnderscore)

    gen_file('%s/sql/%s_setup/mysql4-install-%s.php' %
             (basePluginDir, basePluginWithUnderscoreLowercase, options.version),
             """<?php
$installer = $this;
$installer->startSetup();

$installer->run("
    CREATE TABLE IF NOT EXISTS %s (
        `%s_id` INT(8) NOT NULL AUTO_INCREMENT PRIMARY KEY
    ); 
    
");

$installer->endSetup();""" % (table_name, table_name))


def gen_grid():

    if not options.grid:
        return

    gen_dir('%s/controllers/Adminhtml' % basePluginDir)

    gen_file('%s/controllers/Adminhtml/%sController.php' % (basePluginDir, options.grid), """<?php

class %s_%s_Adminhtml_%sController extends Mage_Adminhtml_Controller_Action
{
    public function indexAction()
    {
        $this->_title($this->__('%s %s'));
        $this->loadLayout();
        // $this->_setActiveMenu(' --- INSERT MENU HERE --- ');
        $this->_addContent($this->getLayout()->createBlock('%s/adminhtml_%s'));
        $this->renderLayout();
    }
    
    public function gridAction() {
        $this->loadLayout();
        $this->getResponse()->setBody(
            $this->getLayout()->createBlock('%s/adminhtml_%s_grid')->toHtml()
        );
    }

}""" % (options.plugin, options.module, options.grid, options.plugin, options.module,
        basePluginWithUnderscoreLowercase, options.grid.lower() , basePluginWithUnderscoreLowercase,
        options.grid))

    gen_dir('%s/Block/Adminhtml/%s/' % (basePluginDir, options.grid))

    gen_file('%s/Block/Adminhtml/%s.php' % (basePluginDir, options.grid), """<?php

class %s_%s_Block_Adminhtml_%s extends Mage_Adminhtml_Block_Widget_Grid_Container
{
    public function __construct()
    {
        $this->_blockGroup = '%s';
        $this->_controller = 'adminhtml_%s';
        $this->_headerText = Mage::helper('%s')->__('%s %s');

        parent::__construct();
        $this->_removeButton('add');

        $this->_addButton('clear', array(
            'label'     => Mage::helper('adminhtml')->__('Clear'),
            'onclick'   => 'window.location.href=\\'' . $this->getUrl('*/*/') . '\\'',
            'class'     => 'delete',
        ));
    }
}
""" % (options.plugin, options.module, options.grid, basePluginWithUnderscoreLowercase, options.grid.lower(),
       basePluginWithUnderscoreLowercase, options.plugin, options.module ))

    gen_file('%s/Block/Adminhtml/%s/Grid.php' % (basePluginDir, options.grid), """<?php

class %s_%s_Block_Adminhtml_%s_Grid extends Mage_Adminhtml_Block_Widget_Grid
{
    public function __construct()
    {
        parent::__construct();
        //$this->setId(' --- TABLE ID HERE --- ');
        $this->setDefaultSort('requested');
        $this->setDefaultDir('DESC');
        $this->setSaveParametersInSession(true);
        $this->setUseAjax(true);
    }

    protected function _prepareCollection() {

        $collection = Mage::getResourceModel('%s/---MODEL---_collection');

        $this->setCollection( $collection );

        return parent::_prepareCollection();
    }

    protected function _prepareColumns()
    {
        $helper = Mage::helper('%s');

        $this->addColumn('id', array(
            'header' => $helper->__('ID'),
            'type' => 'text',
        ));

        return parent::_prepareColumns();
    }

    public function getRowUrl($item) {
        return $this->getUrl("*/*/" . $item->getId() );
    }


    public function getGridUrl()
    {
        return $this->getUrl('*/*/grid', array('_current'=>true));
    }
}""" % (options.plugin, options.module, options.grid,
        basePluginWithUnderscoreLowercase, basePluginWithUnderscoreLowercase ))

    gen_xml_path(configFile, 'config/admin/routers/adminhtml/args/modules/%s' % basePluginWithUnderscoreLowercase,
                 '%s_Adminhtml' % basePluginWithUnderscore)

    gen_xml_path(configFile, 'config/global/blocks/%s/class' % basePluginWithUnderscoreLowercase,
                 basePluginWithUnderscore + '_Block')

    xml = '%s/etc/adminhtml.xml' % basePluginDir

    gen_file(xml, """<?xml version="1.0"?><config></config>""")

    menu_xml_path = 'config/menu/children/%s_%s' % (basePluginWithUnderscoreLowercase, options.grid)

    gen_xml_path(xml, '%s/sort_order' % menu_xml_path, '0')
    gen_xml_path(xml, '%s/title' % menu_xml_path, options.grid.lower())
    gen_xml_path(xml, '%s/action' % menu_xml_path, 'adminhtml/%s' % options.grid.lower())


gen_module()
gen_helper()
gen_collection()
gen_grid()