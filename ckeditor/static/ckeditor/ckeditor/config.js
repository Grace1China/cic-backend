/**
 * @license Copyright (c) 2003-2019, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see https://ckeditor.com/legal/ckeditor-oss-license
 */

CKEDITOR.editorConfig = function( config ) {
	// Define changes to default configuration here. For example:
	// config.language = 'fr';
	// config.uiColor = '#AADC6E';
	config.filebrowserImageBrowseUrl = '/media_browse/?type=images&from=ckeditor_browse';
	config.allowedContent = true;
	config.pasteFilter = null
};
CKEDITOR.editorConfig.allowedContent = true;
CKEDITOR.editorConfig.pasteFilter = null

