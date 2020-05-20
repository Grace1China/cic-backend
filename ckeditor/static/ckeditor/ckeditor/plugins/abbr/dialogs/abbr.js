/**
 * Copyright (c) 2014-2020, CKSource - Frederico Knabben. All rights reserved.
 * Licensed under the terms of the MIT License (see LICENSE.md).
 *
 * The abbr plugin dialog window definition.
 *
 * Created out of the CKEditor Plugin SDK:
 * https://ckeditor.com/docs/ckeditor4/latest/guide/plugin_sdk_sample_1.html
 */

// Our dialog definition.
CKEDITOR.dialog.add( 'abbrDialog', function( editor ) {
	return {

		// Basic properties of the dialog window: title, minimum size.
		title: '媒体库',
		minWidth: 400,
		minHeight: 200,

		// Dialog window content definition.
		contents: [
			{
				// Definition of the Basic Settings dialog tab (page).
				id: 'tab-basic',
				label: '媒体库',

				// The tab content.
				elements: [
					// {
					// 	// Text input field for the abbreviation text.
					// 	type: 'text',
					// 	id: 'abbr',
					// 	label: 'Abbreviation',

					// 	// Validation checking whether the field is not empty.
					// 	validate: CKEDITOR.dialog.validate.notEmpty( "Abbreviation field cannot be empty." ),

					// 	// Called by the main setupContent method call on dialog initialization.
					// 	setup: function( element ) {
					// 		this.setValue( element.getText() );
					// 	},

					// 	// Called by the main commitContent method call on dialog confirmation.
					// 	commit: function( element ) {
					// 		element.setText( this.getValue() );
					// 	}
					// },
					// {
					// 	// Text input field for the abbreviation title (explanation).
					// 	type: 'text',
					// 	id: 'title',
					// 	label: 'Explanation',
					// 	validate: CKEDITOR.dialog.validate.notEmpty( "Explanation field cannot be empty." ),

					// 	// Called by the main setupContent method call on dialog initialization.
					// 	setup: function( element ) {
					// 		this.setValue( element.getAttribute( "title" ) );
					// 	},

					// 	// Called by the main commitContent method call on dialog confirmation.
					// 	commit: function( element ) {
					// 		element.setAttribute( "title", this.getValue() );
					// 	}
					// }
					{
						type: "html",
						html: "<iframe id='myiframe' width='100%' height='100%' src='" + "/media_browse/?type=images&from=ckeditor" + "'></iframe>",
						style: "width:920px;height:580px;padding:0;"
					  }
				]
			},

			// Definition of the Advanced Settings dialog tab (page).
				// {
				// 	id: 'tab-adv',
				// 	label: 'Advanced Settings',
				// 	elements: [
				// 		{
				// 			// Another text field for the abbr element id.
				// 			type: 'text',
				// 			id: 'id',
				// 			label: 'Id',

				// 			// Called by the main setupContent method call on dialog initialization.
				// 			setup: function( element ) {
				// 				this.setValue( element.getAttribute( "id" ) );
				// 			},

				// 			// Called by the main commitContent method call on dialog confirmation.
				// 			commit: function ( element ) {
				// 				var id = this.getValue();
				// 				if ( id )
				// 					element.setAttribute( 'id', id );
				// 				else if ( !this.insertMode )
				// 					element.removeAttribute( 'id' );
				// 			}
				// 		}
					
				// 	]
				// }
		],

		// Invoked when the dialog is loaded.
		onShow: function() {

			// // Get the selection from the editor.
			// var selection = editor.getSelection();

			// // Get the element at the start of the selection.
			// var element = selection.getStartElement();

			// // Get the <abbr> element closest to the selection, if it exists.
			// if ( element )
			// 	element = element.getAscendant( 'abbr', true );

			// // Create a new <abbr> element if it does not exist.
			// if ( !element || element.getName() != 'abbr' ) {
			// 	element = editor.document.createElement( 'abbr' );

			// 	// Flag the insertion mode for later use.
			// 	this.insertMode = true;
			// }
			// else
			// 	this.insertMode = false;

			// // Store the reference to the <abbr> element in an internal property, for later use.
			// this.element = element;

			// // Invoke the setup methods of all dialog window elements, so they can load the element attributes.
			// if ( !this.insertMode )
			// 	this.setupContent( this.element );
		},

		// This method is invoked once a user clicks the OK button, confirming the dialog.
		onOk: function() {

			// // Create a new <abbr> element.
			// var abbr = this.element;

			// // Invoke the commit methods of all dialog window elements, so the <abbr> element gets modified.
			// this.commitContent( abbr );

			// // Finally, if in insert mode, insert the element into the editor at the caret position.
			// if ( this.insertMode )
			// 	editor.insertElement( abbr );
			// var html = `<p><img src="https://bicf-media-destination.oss-cn-beijing.aliyuncs.com/L3/03132020.jpg"></p>`;
			var imgs= document.getElementById('myiframe').contentDocument.querySelectorAll('.el-checkbox.is-checked .mediadata')
			console.log(imgs)

			// //使用JS最基础的getElementById找到我们的iframe控件，然后再获取id为username的控件
			// html = html + "<h2>" + your_name.value + ": </h2>";
			// var selected_books = document.getElementById('myiframe').contentDocument.getElementsByName('yourbook');
			// //使用JS最基础的getElementById找到我们的iframe控件，然后再获取所有name为yourBook的控件
			// var books = "";
			// for(var i=0; i< selected_books.length; i++){
			// 	//遍历我们的selected数组
			// 	if (selected_books[i].checked){
			// 	books = books + "<p> " + selected_books[i].value + "</p>";
			// 	}
			// }
			// html = html + books;

			// console.log(img)
			
			html = ''
			imgs.forEach(function(e){
				typ = e.getAttribute('typ')
				if(typ == 'images'){
					html = html + `<p><img style="width:100%;" src="${e.getAttribute('src').replace('/wh100_auto','')}"></p>` 
				}else if(typ == 'videos'){
					html = html + `<div class="ckeditor-html5-video" style="text-align:center">
						<video controls="controls" controlslist="nodownload"  src="${e.getAttribute('data-src')}" width="100%">&nbsp;</video>
					</div>`
				}else if(typ == 'audios'){
					//html = html + `<p><audio controls="" autoplay="" name="media" src="${e.getAttribute('data-src')}"></audio></p>` 
					html = html + `<div class="ckeditor-html5-video" style="text-align:center">
						<audio controls="controls" controlslist="nodownload" controlslist="nodownload" src="${e.getAttribute('data-src')}" width="100%" type="audio/mpeg">&nbsp;</audio>
					</div>`
				}else if(typ == 'pdfs'){
					html = html + `<p><iframe frameborder="0" scrolling="no" src="${e.getAttribute('data-src')}"></iframe></p>`
				}
			})
			// var sel = editor.getSelection();
			// var range = sel.getRanges()[0];

			// // no range, means the editor is empty. Select the range.
			// if (!range) {
			// range = editor.createRange();
			// range.selectNodeContents( editor.editable() );
			// sel.selectRanges( [ range ] );
			// }
			editor.insertHtml(html);
			this.commitContent();
		},
		onHide: function () {
			document.getElementById('myiframe').contentDocument.location.reload();
		},
	};
});
