(function(){

	// the minimum version of jQuery we want
	var v = "1.3.2";

	// check prior inclusion and version
	if (window.jQuery === undefined || window.jQuery.fn.jquery < v) {
		var done = false;
		var script = document.createElement("script");
		script.src = "http://ajax.googleapis.com/ajax/libs/jquery/" + v + "/jquery.min.js";
		script.onload = script.onreadystatechange = function(){
			if (!done && (!this.readyState || this.readyState == "loaded" || this.readyState == "complete")) {
				done = true;
				initMyBookmarklet();
			}
		};
		document.getElementsByTagName("head")[0].appendChild(script);
	} else {
		initMyBookmarklet();
	}

	function initMyBookmarklet() {
		(window.myBookmarklet = function() {
			// your JavaScript code goes here!
            url = "http://localhost:8000/bookmarklet/idea/";
            /*newwindow=window.open(url,'Idea Board','height=300,width=350');
        	if (window.focus) {
                newwindow.focus()
            }*/
            
            $("body").append('<div id="idea_bookmarklet" style="width:80%; height:400px; text-align:center; position:fixed; top:10%; left:10%; z-index:1000; background-color:white; rgba:(240,240,240,0.25);">'
                             +'<iframe id="the_frame" width="400" height="400" src="http://localhost:8000/bookmarklet/idea/" onload="$(\'#wikiframe iframe\').slideDown(500);">Enable iFrames.</iframe>'
                             +'<a href="" id="close_idea_bookmarklet">Close</a>'
                             +'</div>'
                            );
            $("#close_idea_bookmarklet").click(function(event){
                event.preventDefault();
                $("#idea_bookmarklet").remove();
            });
    


		})();
	}

})();

