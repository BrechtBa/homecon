/*
    Copyright 2015 Brecht Baeten
    This file is part of KNXControl.

    KNXControl is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    KNXControl is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with KNXControl.  If not, see <http://www.gnu.org/licenses/>.
*/

pagebuilder = {
//model
	section: [],
// methods
	add_section: function(){
		pagebuilder.section.push({
			id: '',
			name: '',
			page: []
		});
	},
	update_section: function(id,name){
		this.id = id;
		this.name = name;
	},
	delete_section: function(id){
		pagebuilder.section.splice(id,1);
	},
	move_section_up: function(id){
		var new_id = id;
		if(id>0){
			var temp = pagebuilder.section[id];
			pagebuilder.section[id] = pagebuilder.section[id-1];
			pagebuilder.section[id-1] = temp;
			new_id = new_id-1;
		}
		return new_id;
	},
	move_section_down: function(id){
		var new_id = id;
		if(id<pagebuilder.section.length-1){
			var temp = pagebuilder.section[id];
			// -1+2 so it doesn't get treated as a string
			pagebuilder.section[id] = pagebuilder.section[id-1+2];
			pagebuilder.section[id-1+2] = temp;
			new_id = new_id-1+2;
		}
		return new_id;
	},
	add_page: function(section){
		section.page.push({
			id: '',
			name: '',
			img: 'scene_livingroom.png',
			temperature_item:'',
			section: [],
		});
	},
	update_page: function(page,id,name,img,temperature_item){
		page.id = id;
		page.name = name;
		page.img = img;
		page.temperature_item = temperature_item;
	},
	delete_page: function(section,id){
		section.page.splice(id,1);
	},
	move_page_up: function(section,id){
		var new_id = id;
		if(id>0){
			var temp = section.page[id];
			section.page[id] = section.page[id-1];
			section.page[id-1] = temp;
			new_id = id - 1;
		}
		return new_id;
	},
	move_page_down: function(section,id){
		var new_id = id;
		if(id<section.page.length-1){
			var temp = section.page[id];
			// -1+2 so it doesn't get treated as a string
			section.page[id] = section.page[id-1+2];
			section.page[id-1+2] = temp;
			new_id = new_id-1+2;
		}
		return new_id;
	},
	add_page_section: function(page){
		page.section.push({
			name: '',
			type: 'collapsible',
			widget: []
		});
	},
	update_page_section: function(section,name,type){
		section.name = name;
		section.type = type;
	},
	delete_page_section: function(page,id){
		page.section.splice(id,1);
	},
	move_page_section_up: function(page,id){
		var new_id = id;
		if(id>0){
			var temp = page.section[id];
			page.section[id] = page.section[id-1];
			page.section[id-1] = temp;
			new_id = id - 1;
		}
		return new_id;
	},
	move_page_section_down: function(page,id){
		var new_id = id;
		if(id<page.section.length-1){
			var temp = page.section[id];
			// -1+2 so it doesn't get treated as a string
			page.section[id] = page.section[id-1+2];
			page.section[id-1+2] = temp;
			new_id = id -1+2;
		}
		return new_id;
	},
	add_widget: function(section,type){
		section.widget.push({
			type: type,
			options: JSON.parse(JSON.stringify($.knxcontrol[type].prototype.options))
		});
	},
	update_widget: function(widget,type,options){
		widget.type = type;
		widget.options = options;
	},
	delete_widget: function(page_section,id){
		page_section.widget.splice(id,1);
	},
	move_widget_up: function(page_section,id){
		var new_id = id;
		if(id>0){
			var temp = page_section.widget[id];
			page_section.widget[id] = page_section.widget[id-1];
			page_section.widget[id-1] = temp;
			new_id = id - 1;
		}
		return new_id;
	},
	move_widget_down: function(page_section,id){
		var new_id = id;
		if(id<page_section.widget.length-1){
			var temp = page_section.widget[id];
			// -1+2 so it doesn't get treated as a string
			page_section.widget[id] = page_section.widget[id-1+2];
			page_section.widget[id-1+2] = temp;
			new_id = id - 1+2;
		}
		return new_id;
	},
	save: function(){
		$.post('requests/update_table.php',{table: 'pagebuilder', column: 'model', value: JSON.stringify(pagebuilder.section), where: 'id=1'},function(result){
			console.log('saved');
		});
	},
	publish: function(){
		var publish = '';
		$.each(pagebuilder.section,function(section_index,section){
			$.each(section.page,function(page_index,page){
				publish += publish_page(section_index,page_index);
			});
		});
		$.post('requests/pagebuilder_publish.php',{page: 'pages', model: publish},function(result){
			console.log('published pages');
		
			publish = publish_menu();
			$.post('requests/pagebuilder_publish.php',{page: 'menu', model: publish},function(result){
				console.log('published menu');
			
				$("#message_popup").html('<h3>Model published</h3>');
				$("#message_popup").popup('open');
				setTimeout(function(){$("#message_popup").popup('close');}, 500);
			});
		});
	},	
	widgetlist:{
		clock: {name: 'Clock'},
		line: {name: 'Separator'},
		lightswitch: {name: 'Light switch'},
		lightdimmer: {name: 'Light dimmer'},
		shading: {name: 'Shading control'},
		alarm: {name: 'Alarm'},
		chart: {name: 'Chart'},
		displayvalue: {name: 'Display value'},
		btn: {name: 'Button'}
	},
	iconlist:[
		'fts_sunblind.png',
		'light_light.png',
		'measure_current.png',
		'measure_photovoltaic_inst.png',
		'measure_power.png',
		'measure_power_meter.png',
		'measure_voltage.png',
		'measure_water_meter.png',
		'sani_heating.png',
		'sani_heating_automatic.png',
		'sani_heating_manual.png',
		'sani_heating_temp.png',
		'sani_solar.png',
		'sani_water_tap.png',
		'scene_baby.png',
		'scene_baking_oven.png',
		'scene_bath.png',
		'scene_bathroom.png',
		'scene_childs_room.png',
		'scene_cinema.png',
		'scene_cleaning.png',
		'scene_clothes_dryer.png',
		'scene_cockle_stove.png',
		'scene_cooking.png',
		'scene_cooking_hob.png',
		'scene_corridor.png',
		'scene_cubby.png',
		'scene_day.png',
		'scene_dinner.png',
		'scene_dishwasher.png',
		'scene_dressing_room.png',
		'scene_drink.png',
		'scene_fitness.png',
		'scene_fountain.png',
		'scene_gaming.png',
		'scene_garden.png',
		'scene_hall.png',
		'scene_keyboard.png',
		'scene_laundry_room.png',
		'scene_laundry_room_fem.png',
		'scene_livingroom.png',
		'scene_making_love_clean.png',
		'scene_microwave_oven.png',
		'scene_night.png',
		'scene_office.png',
		'scene_party.png',
		'scene_pool.png',
		'scene_robo_lawnmower.png',
		'scene_robo_vac_cleaner.png',
		'scene_sauna.png',
		'scene_scene.png',
		'scene_shower.png',
		'scene_sleeping.png',
		'scene_sleeping_alternat.png',
		'scene_sleeping_twin_0_0.png',
		'scene_sleeping_twin_0_1.png',
		'scene_sleeping_twin_1_0.png',
		'scene_sleeping_twin_1_1.png',
		'scene_stairs.png',
		'scene_storeroom.png',
		'scene_stove.png',
		'scene_summerhouse.png',
		'scene_swimming.png',
		'scene_terrace.png',
		'scene_toilet.png',
		'scene_toilet_alternat.png',
		'scene_visit_guests.png',
		'scene_washing_machine.png',
		'scene_wine_cellar.png',
		'scene_workshop.png',
		'scene_x-mas.png',
		'status_automatic.png',
		'time_calendar.png',
		'time_clock.png',
		'time_statistic.png',
		'time_timer.png',
		'time_timer_switch.png',
		'vent_ventilation.png',
		'weather_cloudy.png',
		'weather_cloudy_heavy.png',
		'weather_cloudy_light.png',
		'weather_directions.png',
		'weather_frost.png',
		'weather_rain.png',
		'weather_snow_light.png',
		'weather_station.png'
	]
};

/*****************************************************************************/
/*                     views                                                 */
/*****************************************************************************/
render_page = function(section_id,page_id){
	// save
	pagebuilder.save();
	
	// start rendering
	page = pagebuilder.section[section_id].page[page_id];
	
	var select_widget_values = {};
	// if the page is rebuilt get the widget select values
	$.each($('#renderpage').find('select.select_widget'),function(index,select){
		select_widget_values[$(select).parents('section').attr('data-id')] = $(select).val();
	});

	// add the page elements to the DOM for temporary displaying
	// clear the container and start fresh
	$('#renderpage').empty();
	$('#renderpage').attr('data-section_id',section_id);
	$('#renderpage').attr('data-page_id',page_id);
	
	
	// add header
	if(page.id != 'home'){
		$('#renderpage').append('<header><img src="icons/ws/'+page.img+'"><h1>'+page.name+'</h1></header>');
		if(page.temperature_item != ''){
			$('#renderpage header').append('<div class="value"><span data-role="displayvalue" data-item="'+page.temperature_item+'" data-digits="1"></span>&deg;C</div>');
		}
	}
	
	// pagesections
	$.each(page.section,function(index,section){
		if(section.type=='collapsible'){
			$('#renderpage').append('<section data-role="collapsible" data-theme="a" data-collapsed="false" data-id="'+index+'"><h1>'+section.name+'</h1></section>');
		}
		else if(section.type=='collapsed'){
			$('#renderpage').append('<section data-role="collapsible" data-theme="a" data-collapsed="true" data-id="'+index+'"><h1>'+section.name+'</h1></section>');
		}
		else{
			$('#renderpage').append('<section data-id="'+index+'"></section>');
		}
		$('#renderpage section[data-id="'+index+'"]').append('<a href"#" class="edit_page_section" data-role="button" data-rel="popup" data-icon="grid" data-mini="true" data-iconpos="notext" data-inline="true">Edit</a>');
		
		// widgets
		section_index = index;
		$.each(section.widget,function(index,widget){
			$('#renderpage section[data-id="'+section_index+'"]').append('<div data-role="'+widget.type+'" data-id="'+index+'"><a href"#" class="edit_widget" data-role="button" data-rel="popup" data-icon="grid" data-mini="true" data-iconpos="notext" data-inline="true">Edit</a></div>');
			
			// widget options
			widget_index = index;
			$.each(widget.options,function(index,option){
				$('#renderpage section[data-id="'+section_index+'"] div[data-id="'+widget_index+'"]').attr('data-'+index,option);
			});
			
		});
		// widget adding
		$('#renderpage section[data-id="'+section_index+'"]').append('<fieldset class="ui-grid-a"><div class="ui-block-a"><select class="select_widget" data-native-menu="false"><option>Select Widget</option></select></div><div class="ui-block-b"><a href="#" class="add_widget" data-role="button" data-id="'+page.id+'">Add</a></div>');
		$.each(pagebuilder.widgetlist,function(index,widget){
			$('#renderpage section[data-id="'+section_index+'"] select').append('<option value="'+index+'">'+widget.name+'</option>');
		});
		if(index in select_widget_values){
			$('#renderpage section[data-id="'+section_index+'"] select').val(select_widget_values[index]);
		}
	});
	$('#renderpage').append('<a href="#" class="add_page_section" data-role="button" data-id="'+page.id+'">Add section</a>');
	
	// enhance
	$('#renderpage').enhanceWithin();
}
	
render_menu = function(){
	// save
	pagebuilder.save();
	
	// start rendering
	$('#rendermenu').empty();

	// sections
	$.each(pagebuilder.section,function(index,section){
		if(section.id=='home'){
			$('#rendermenu').append('<section data-id="'+index+'"><ul data-role="listview" data-inset="false" data-icon="false" data-theme="b"></ul></section>');
		}
		else{
			$('#rendermenu').append('<section data-id="'+index+'"><ul data-role="listview" data-inset="false" data-icon="false" data-theme="b"><li class="devider" data-theme="a"><a href="#"><h1>'+section.name+'</h1></a><a class="edit_section" data-icon="grid" data-iconpos="notext">Edit</a></li></ul><a href="#" class="add_page" data-role="button">Add page</a></section>');
		}
		//pages
		section_index = index;
		$.each(section.page,function(index,page){
			if(section.id=='home'){
				$('#rendermenu section[data-id="'+section_index+'"] ul').append('<li data-id="'+index+'"><a href="#" class="renderpage"><h1>'+page.name+'</h1></a></li>');
			}
			else{
				$('#rendermenu section[data-id="'+section_index+'"] ul').append('<li data-id="'+index+'"><a href="#" class="renderpage"><img src="icons/ws/'+page.img+'" data-id="'+index+'" ><h1>'+page.name+'</h1></a><a href="#" class="edit_page" data-inline="true" data-icon="grid" data-iconpos="notext">Edit</a></li>');
			}
		});
		
	});
	$('#rendermenu').append('<a href="#" class="add_section" data-role="button">Add section</a>');
	
	// enhance
	$('#menu').enhanceWithin();
}


/*****************************************************************************/
/*                     controls                                              */
/*****************************************************************************/
/* Adding                                                                    */
$(document).on('click','a.add_section',function(){
	pagebuilder.add_section();
	render_menu();
});
$(document).on('click','a.add_page',function(){
	var id = $(this).parents('section').attr('data-id')
	pagebuilder.add_page(pagebuilder.section[id]);
	render_menu();
});
$(document).on('click','a.add_page_section',function(){
	var section_id = $('#renderpage').attr('data-section_id');
	var id = $('#renderpage').attr('data-page_id');
	pagebuilder.add_page_section(pagebuilder.section[section_id].page[id]);
	render_page(section_id,id);
});
$(document).on('click','a.add_widget',function(){

	var section_id = $(this).parents('#renderpage').attr('data-section_id');
	var page_id = $(this).parents('#renderpage').attr('data-page_id');
	var page_section_id = $(this).parents('section').attr('data-id');
	
	var widget_type = $(this).parents('section').find('select.select_widget').val();

	if(widget_type!='Select Widget'){
		pagebuilder.add_widget(pagebuilder.section[section_id].page[page_id].section[page_section_id],widget_type);
		render_page(section_id,page_id);
	}
});


/* Editing                                                                   */
$(document).on('click','a.edit_section',function(){
	var id = $(this).parents('section').attr('data-id');
	$('#section_def_popup').popup('open');
	$('#section_def_popup').attr('data-id',id);
	$('#section_def_popup input[data-field="name"]').val(pagebuilder.section[id].name);
});
$(document).on('click','a.edit_page',function(){
	var section_id = $(this).parents('section').attr('data-id');
	var id = $(this).parents('li').attr('data-id');
	$('#page_def_popup').popup('open');
	$('#page_def_popup').attr('data-section_id',section_id);
	$('#page_def_popup').attr('data-id',id);

	$('#page_def_popup select[data-field="img"]').empty();
	$.each(pagebuilder.iconlist,function(index,icon){
		$('#page_def_popup select[data-field="img"]').append('<option value="'+icon+'">'+icon+'</option>')
	});
	$('#page_def_popup input[data-field="name"]').val(pagebuilder.section[section_id].page[id].name);
	$('#page_def_popup select[data-field="img"]').val(pagebuilder.section[section_id].page[id].img).selectmenu('refresh');
});
$(document).on('click','a.edit_page_section',function(){
	var id = $(this).parents('section').attr('data-id');
	var section_id = $('#renderpage').attr('data-section_id');
	var page_id = $('#renderpage').attr('data-page_id');
	$('#page_section_def_popup').popup('open');
	$('#page_section_def_popup').attr('data-id',id);
	$('#page_section_def_popup input[data-field="name"]').val(pagebuilder.section[section_id].page[page_id].section[id].name);
	$('#page_section_def_popup select[data-field="type"]').val(pagebuilder.section[section_id].page[page_id].section[id].type).selectmenu('refresh');
});
$(document).on('click','a.edit_widget',function(){
	var id = $(this).parents('div[data-role]').attr('data-id');
	var section_id = $('#renderpage').attr('data-section_id');
	var page_id = $('#renderpage').attr('data-page_id');
	var page_section_id = $(this).parents('section').attr('data-id');
	var type = $(this).parents('div[data-role]').attr('data-role');
	
	$('#widget_def_popup').popup('open');
	$('#widget_def_popup').attr('data-id',id);
	$('#widget_def_popup').attr('data-page_section_id',page_section_id);
	$('#widget_def_popup div.options').empty();
	$.each(pagebuilder.section[section_id].page[page_id].section[page_section_id].widget[id].options,function(index,option){
		if( !(index=='disabled' || index=='create') ){
			$('#widget_def_popup div.options').append('<input type="text" data-field="'+index+'" value="'+option+'" placeholder="'+index+'">');
		}
		$('#widget_def_popup div.options').enhanceWithin();
	});
});



/* Saving                                                                    */
$(document).on('click','#section_def_popup a.save',function(){
	var section_id = $('#section_def_popup').attr('data-id');
	$('#section_def_popup').popup('close');
	pagebuilder.section[section_id].name = $('#section_def_popup input[data-field="name"]').val();
	pagebuilder.section[section_id].id = $('#section_def_popup input[data-field="name"]').val().toLowerCase();
	render_menu();
});
$(document).on('click','#page_def_popup a.save',function(){
	var section_id = $('#page_def_popup').attr('data-section_id');
	var id = $('#page_def_popup').attr('data-id');
	$('#page_def_popup').popup('close');
	pagebuilder.section[section_id].page[id].name = $('#page_def_popup input[data-field="name"]').val();
	pagebuilder.section[section_id].page[id].id = $('#page_def_popup input[data-field="name"]').val().toLowerCase();
	pagebuilder.section[section_id].page[id].img = $('#page_def_popup select[data-field="img"]').val();
	render_menu();
});
$(document).on('click','#page_section_def_popup a.save',function(){
	var id = $('#page_section_def_popup').attr('data-id');
	var section_id = $('#renderpage').attr('data-section_id');
	var page_id = $('#renderpage').attr('data-page_id');
	$('#page_section_def_popup').popup('close');
	pagebuilder.section[section_id].page[page_id].section[id].name = $('#page_section_def_popup input[data-field="name"]').val();
	pagebuilder.section[section_id].page[page_id].section[id].type = $('#page_section_def_popup select[data-field="type"]').val();
	render_page(section_id,page_id);
});
$(document).on('click','#widget_def_popup a.save',function(){
	var id = $('#widget_def_popup').attr('data-id');
	var page_section_id = $('#widget_def_popup').attr('data-page_section_id');
	var section_id = $('#renderpage').attr('data-section_id');
	var page_id = $('#renderpage').attr('data-page_id');
	$('#widget_def_popup').popup('close');
	$.each($('#widget_def_popup div.options input'),function(index,option){
		index = $(option).attr('data-field');
		pagebuilder.section[section_id].page[page_id].section[page_section_id].widget[id].options[index] = $(option).val();
	});
	render_page(section_id,page_id);
});

/* Deleting                                                                  */
$(document).on('click','#section_def_popup a.delete',function(){
	var section_id = $('#section_def_popup').attr('data-id');
	$('#section_def_popup').popup('close');
	pagebuilder.delete_section(section_id);
	render_menu();
});
$(document).on('click','#page_def_popup a.delete',function(){
	var section_id = $('#page_def_popup').attr('data-section_id');
	var id = $('#page_def_popup').attr('data-id');
	$('#page_def_popup').popup('close');
	pagebuilder.delete_page(pagebuilder.section[section_id],id);
	render_menu();
});
$(document).on('click','#page_section_def_popup a.delete',function(){
	var id = $('#page_section_def_popup').attr('data-id');
	var section_id = $('#renderpage').attr('data-section_id');
	var page_id = $('#renderpage').attr('data-page_id');
	$('#page_section_def_popup').popup('close');
	pagebuilder.delete_page_section(pagebuilder.section[section_id].page[page_id],id);
	render_page(section_id,page_id);
});
$(document).on('click','#widget_def_popup a.delete',function(){
	var id = $('#widget_def_popup').attr('data-id');
	var page_section_id = $('#widget_def_popup').attr('data-page_section_id');
	var section_id = $('#renderpage').attr('data-section_id');
	var page_id = $('#renderpage').attr('data-page_id');
	$('#widget_def_popup').popup('close');
	pagebuilder.delete_widget(pagebuilder.section[section_id].page[page_id].section[page_section_id],id);
	render_page(section_id,page_id);
});

/* Moving                                                                    */
$(document).on('click','#section_def_popup a.move_up',function(){
	var id = $('#section_def_popup').attr('data-id');
	new_id = pagebuilder.move_section_up(id);
	$('#section_def_popup').attr('data-id',new_id);
	render_menu();
});
$(document).on('click','#section_def_popup a.move_down',function(){
	var id = $('#section_def_popup').attr('data-id');
	new_id = pagebuilder.move_section_down(id);
	$('#section_def_popup').attr('data-id',new_id);
	render_menu();
});

$(document).on('click','#page_def_popup a.move_up',function(){
	var section_id = $('#page_def_popup').attr('data-section_id');
	var id = $('#page_def_popup').attr('data-id');
	new_id = pagebuilder.move_page_up(pagebuilder.section[section_id],id);
	$('#page_def_popup').attr('data-id',new_id);
	render_menu();
});
$(document).on('click','#page_def_popup a.move_down',function(){
	var section_id = $('#page_def_popup').attr('data-section_id');
	var id = $('#page_def_popup').attr('data-id');
	new_id = pagebuilder.move_page_down(pagebuilder.section[section_id],id);
	$('#page_def_popup').attr('data-id',new_id);
	render_menu();
});

$(document).on('click','#page_section_def_popup a.move_up',function(){
	var id = $('#page_section_def_popup').attr('data-id');
	var section_id = $('#renderpage').attr('data-section_id');
	var page_id = $('#renderpage').attr('data-page_id');
	new_id = pagebuilder.move_page_section_up(pagebuilder.section[section_id].page[page_id],id);
	$('#page_section_def_popup').attr('data-id',new_id);
	render_page(section_id,page_id);
});
$(document).on('click','#page_section_def_popup a.move_down',function(){
	var id = $('#page_section_def_popup').attr('data-id');
	var section_id = $('#renderpage').attr('data-section_id');
	var page_id = $('#renderpage').attr('data-page_id');
	new_id = pagebuilder.move_page_section_down(pagebuilder.section[section_id].page[page_id],id);
	$('#page_section_def_popup').attr('data-id',new_id);
	render_page(section_id,page_id);
});

$(document).on('click','#widget_def_popup a.move_up',function(){
	var id = $('#widget_def_popup').attr('data-id');
	var page_section_id = $('#widget_def_popup').attr('data-page_section_id');
	var section_id = $('#renderpage').attr('data-section_id');
	var page_id = $('#renderpage').attr('data-page_id');
	new_id = pagebuilder.move_widget_up(pagebuilder.section[section_id].page[page_id].section[page_section_id],id);
	$('#widget_def_popup').attr('data-id',new_id);
	render_page(section_id,page_id);
});
$(document).on('click','#widget_def_popup a.move_down',function(){
	var id = $('#widget_def_popup').attr('data-id');
	var page_section_id = $('#widget_def_popup').attr('data-page_section_id');
	var section_id = $('#renderpage').attr('data-section_id');
	var page_id = $('#renderpage').attr('data-page_id');
	new_id = pagebuilder.move_widget_down(pagebuilder.section[section_id].page[page_id].section[page_section_id],id);
	$('#widget_def_popup').attr('data-id',new_id);
	render_page(section_id,page_id);
});






/*****************************************************************************/
/*                     rendermenu controls                                   */
/*****************************************************************************/
$(document).on('click','#rendermenu a.renderpage',function(){
	var section_id = $(this).parents('section').attr('data-id');
	var id = $(this).parents('li').attr('data-id');
	render_page(section_id,id);
});








/*****************************************************************************/
/*                     global controls                                       */
/*****************************************************************************/
$(document).on('pageinit','#home_pagebuilder',function(){
	
	$.post('requests/select_from_table.php',{table: 'pagebuilder', column: 'model', where: 'id=1'},function(result){
		var model = JSON.parse(result);
		
		pagebuilder.section = JSON.parse(model[0].model);
	
		render_menu();
		render_page(0,0);
		$('#menu').panel("open");	
	});
});
$(document).on('click','nav div.pagebuilder a.export',function(){
	window.open('requests/pagebuilder_export.php?model='+JSON.stringify(pagebuilder.section));
	console.log('export');
});
$(document).on('click','nav div.pagebuilder a.import',function(){
    $('#pagebuilder_import').click();
});
$(document).on('change','#pagebuilder_import',function(event){
	console.log('import');
	
	var reader = new FileReader();
	reader.onload = function(e) {
		var data = e.target.result;
		data = data.replace("data:text/plain;base64,","");

		pagebuilder.section = JSON.parse( window.atob(data) );
		render_menu();
		render_page(0,0);
	};
	reader.readAsDataURL(event.target.files[0]);
	
});
$(document).on('click','nav div.pagebuilder a.publish',function(){
	pagebuilder.publish();
});


/*****************************************************************************/
/*                     Publish                                               */
/*****************************************************************************/
publish_page = function(section_id,page_id){
	section = pagebuilder.section[section_id];
	page = pagebuilder.section[section_id].page[page_id];
	
	var publish = '';
	
	publish += '<!-- This file was automatically generated by KNXControl -->%n%n';
	publish += '%t%t<div id="'+section.id+'_'+page.id+'" data-role="page" data-theme="b" data-section_id="'+section_id+'" data-page_id="'+page_id+'">%n';
	publish += '%t%t%t<div data-role="content">%n';
	
	// add header
	if(page.id != 'home'){
		publish += '%t%t%t%t<header>%n%t%t%t%t%t<img src="icons/ws/'+page.img+'">%n%t%t%t%t%t<h1>'+page.name+'</h1>%n';
		if(page.temperature_item != ''){
			publish += '%t%t%t%t%t<div class="value"><span data-role="displayvalue" data-item="'+page.temperature_item+'" data-digits="1"></span>&deg;C</div>%n';
		}
		publish += '%t%t%t%t</header>%n';
	}
	
	// pagesections
	$.each(page.section,function(index,section){
		if(section.type=='collapsible'){
			publish += '%t%t%t%t<section data-role="collapsible" data-theme="a" data-collapsed="false" data-id="'+index+'">%n%t%t%t%t%t<h1>'+section.name+'</h1>%n';
		}
		else if(section.type=='collapsed'){
			publish += '%t%t%t%t<section data-role="collapsible" data-theme="a" data-collapsed="true" data-id="'+index+'">%n%t%t%t%t%t<h1>'+section.name+'</h1>%n';
		}
		else{
			publish += '%t%t%t%t<section data-id="'+index+'">%n';
		}

		// widgets
		section_index = index;
		$.each(section.widget,function(index,widget){
			publish += '%t%t%t%t%t<div data-role="'+widget.type+'" data-id="'+index+'"';
			
			// widget options
			widget_index = index;
			$.each(widget.options,function(index,option){
				if( !(index=='disabled' || index=='create') ){
					publish += ' data-'+index+'="'+option+'"';
				}
			});
			
			publish+= '></div>%n';
		});
		publish += '%t%t%t%t</section>%n'
	});
	publish += '%t%t%t</div>%n';
	publish += '%t%t</div>%n'
	
	return publish;
}
publish_menu = function(){

	var publish = '';
	publish += '<!-- This file was automatically generated by KNXControl -->%n%n';
	publish += '%t%t<div id="menu" class="menupanel" data-role="panel" data-display="overlay" data-position="left" data-theme="b">%n';
	publish += '%t%t%t<nav id="mainmenu" data-role="collapsible-set" data-corners="false" data-inset="false">%n';
	
	// sections
	$.each(pagebuilder.section,function(index,section){
		if(section.id!='home'){

			publish += '%t%t%t%t<section data-id="'+index+'" data-role="collapsible" data-section="'+section.id+'" data-theme="a" data-content-theme="b"">%n%t%t%t%t%t<h1>'+section.name+'</h1>%n%t%t%t%t%t<ul data-role="listview" data-inset="false">%n';
		
			//pages
			section_index = index;
			$.each(section.page,function(index,page){
				publish += '%t%t%t%t%t%t<li><a href="#'+section.id+'_'+page.id+'"><img src="icons/ws/'+page.img+'"><h1>'+page.name+'</h1></a></li>%n';
			});
			publish += '%t%t%t%t%t</ul>%n';
			publish += '%t%t%t%t</section>%n';
		}
	});
	publish += '%t%t%t</nav>%n';
	publish += '%t%t%t<nav id="rendermenu"></nav>%n';
	publish += '%t%t</div>%n';
	
	return publish;
}