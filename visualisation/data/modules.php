


		<div id='users' data-role='page' data-theme='b'>
			<div data-role='content'>
		

			</div>
		</div>
		
		
		<div id='alarms' data-role='page' data-theme='b'>
			<div data-role='content'>
				<header>
					<img src='icons/ws/control_alarm.png'>
					<h1>Alarms</h1>
				</header>
				
				<section data-role='collapsible' data-theme='a' data-collapsed='false'>
					<h1>Actions</h1>
					<div data-role='action_list'>
					</div>
				</section>
				
			</div>
		</div>
		
		
		<div id='measurements' data-role='page' data-theme='b'>
			<div data-role='content'>
				<header>
					<img src='icons/ws/measure_power_meter.png'>
					<h1>Measurements</h1>
				</header>
				
				<section data-role='collapsible' data-theme='a' data-collapsed='false'>
					<h1>Measurements</h1>
					<div data-role='measurement_list'>
					</div>
				</section>
				
			</div>
		</div>
		
		
		<div id='action_def_popup' class='ui-content' data-role='popup' data-position-to='window' data-theme='b' data-overlay-theme='b'>
			<div data-role='fieldcontain'>
				<label for='action_def_popup_name'>Name:</label>
				<input type='text' id='action_def_popup_name' data-field='name'>
			</div>	
			<div data-role='fieldcontain'>
				<label for='action_def_popup_section'>Section filter:</label>
				<input type='text' id='action_def_popup_section' data-field='section_id'>
			</div>	
			
			<div class='ui-grid-b action_def_list'>
				<div class='ui-block-a'>
					Delay:
				</div>
				<div class='ui-block-b'>
					Items:
				</div>
				<div class='ui-block-c'>
					Value:
				</div>
				<div class='ui-block-a'>
					<input type='number' data-field='delay1' value='0'>
				</div>
				<div class='ui-block-b'>
					<input type='text' data-field='item1'>
				</div>
				<div class='ui-block-c'>
					<input type='text' data-field='value1'>
				</div>
				<div class='ui-block-a'>
					<input type='number' data-field='delay2'>
				</div>
				<div class='ui-block-b'>
					<input type='text' data-field='item2'>
				</div>
				<div class='ui-block-c'>
					<input type='text' data-field='value2'>
				</div>
				<div class='ui-block-a'>
					<input type='number' data-field='delay3'>
				</div>
				<div class='ui-block-b'>
					<input type='text' data-field='item3'>
				</div>
				<div class='ui-block-c'>
					<input type='text' data-field='value3'>
				</div>
				<div class='ui-block-a'>
					<input type='number' data-field='delay4'>
				</div>
				<div class='ui-block-b'>
					<input type='text' data-field='item4'>
				</div>
				<div class='ui-block-c'>
					<input type='text' data-field='value4'>
				</div>
				<div class='ui-block-a'>
					<input type='number' data-field='delay5'>
				</div>
				<div class='ui-block-b'>
					<input type='text' data-field='item5'>
				</div>
				<div class='ui-block-c'>
					<input type='text' data-field='value5'>
				</div>
			</div>
			<a id='action_def_popup_save' data-role='button' data-id='1'>Save</a>
			<a href="#" data-rel="back" data-role="button" data-theme="b" data-icon="delete" data-iconpos="notext" class="ui-btn-right">Close</a>
		</div>
		
		<div id='measurement_def_popup' class='ui-content' data-role='popup' data-position-to='window' data-theme='b' data-overlay-theme='b'>
			<div data-role='fieldcontain'>
				<label for='measurement_def_popup_name'>Name:</label>
				<input type='text' id='measurement_def_popup_name' data-field='name'>
			</div>	
			<div data-role='fieldcontain'>
				<label for='measurement_def_popup_item'>Item:</label>
				<input type='text' id='measurement_def_popup_item' data-field='item'>
			</div>
			<div data-role='fieldcontain'>
				<label for='measurement_def_popup_quantity'>Quantity:</label>
				<input type='text' id='measurement_def_popup_quantity' data-field='quantity'>
			</div>	
			<div data-role='fieldcontain'>
				<label for='measurement_def_popup_unit'>Unit:</label>
				<input type='text' id='measurement_def_popup_unit' data-field='unit'>
			</div>
			<div data-role='fieldcontain'>
				<label for='measurement_def_popup_description'>Description:</label>
				<input type='text' id='measurement_def_popup_description' data-field='description'>
			</div>
			<a id='measurement_def_popup_save' data-role='button' data-id='1'>Save</a>
			<a href="#" data-rel="back" data-role="button" data-theme="b" data-icon="delete" data-iconpos="notext" class="ui-btn-right">Close</a>
		</div>