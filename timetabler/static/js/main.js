function formatPreview(str) {

	var mapObj = {
		code : "M3P17",
		name : "Algebraic Combinatorics",
		type : "Lecture"
	};

	return str.replace(/\{code\}|\{name\}|\{type\}/gi, function(matched) {
		return mapObj[matched.substring(1, matched.length-1)];
	});

}

$(function() { // onload

	$('.btn').button();

	// settings
	$('#settings-icon').click(function() {

		$('#settings').slideToggle(600);
		$('#settings-icon').toggleClass('gray');

	});

	$('#eventtitle').tooltip();
	$('#eventtitle').on('input', function(){

		$('#titlepreview').html(formatPreview($('#eventtitle').val()));

	});

	$.each($('.select-yt'), function(index, value) {
		$(this).val($(this).data('currentYt'));
	});

	// get modules onload and init isotope

	var $container = $('#container');

	$.getJSON($SCRIPT_ROOT + '/module_list', function(data) {

		var html = '<div class="btn-group-vertical" data-toggle="buttons">',
			color_class;

        $.each(data.modules, function(index, module) {

			if(/^M[12345][PFG]($|[0-9ML])/.test(module.code)) {
				color_class = 'pure';
			} else if (/^M[12345]M?S($|[0-9])/.test(module.code)) {
				color_class = 'statistics';
			} else if (/^M[12345][HRT]/.test(module.code)) {
				color_class = "misc_purple"
			}	else {
				color_class = 'applied';
			}

			html += '<div class="btn-module m' + module.code[1] + ' ' + color_class + '" id="' + module.id + '"><p class="mcode">' + module.code + '</p><p class="mname">' + module.name + '</p></div>';
        });

		$("#container").html(html);

		$container.isotope({
			itemSelector: '.btn-module'
		});

	});

	$('#container').data('loaded', 1);

	// filter btns

	var filters = {};

	$('#filters').on('click', 'label.btn-default', function() {

		var $btnGroup = $(this).parents('.btn-group'),
			group = $btnGroup.attr('data-filter-group'),
			isoFilters = [],
			prop;

		filters[group] = $(this).attr('data-filter');

		for(prop in filters) {
			if(filters.hasOwnProperty(prop)) {
				isoFilters.push(filters[prop]);
			}
		}

		$container.isotope({ filter: isoFilters.join('') });

	});

	$('#container').on('click', '.btn-module', function() {

		$(this).toggleClass('keep');

	});

	// download btn

	$('#download').click(function() {

		var errmsg = '',
			num_checked = 0,
			categories = [],
			ids = $.map($('.keep.btn-module'), function(value) {
				return value.id;
			});

		if(!ids.length){
			errmsg += '<div class="alert alert-danger">You haven\'t selected any modules</div>';
		}

		$.each($('.include'), function(index, value) {
			categories.push(value.value);
			num_checked += value.checked;
		});

		if(!num_checked){
			errmsg += '<div class="alert alert-danger">You need to include an event type</div>';
		}

		if(errmsg) {
			$('#errors').html(errmsg);
			$('#errors').show();
			return;
		}

		$('#errors').hide();

		$.getJSON($SCRIPT_ROOT + '/generate', {
			ids: ids,
			categories: categories,
			titleformat: $('#eventtitle').val()
		}, function(data) {
			location.href = '/ics/' + data.filename;
		});

	});

});
