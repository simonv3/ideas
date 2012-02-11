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
            url = "http://ideas.vansintjan.net/bookmarklet/idea/";
            url = "http://localhost:8000/bookmarklet/idea/";
           
             $("body").append(""
                              
                              +'<div id="idea_bookmarklet" style="border-radius:6px; box-shadow:2px 2px 2px #9f9f9f; border:1px solid #a9a9a9; width:60%; height:400px; text-align:center; position:fixed; top:10%; left:20%; z-index:1000; background-color:white; rgba:(240,240,240,0.25);">'
                              
                             +'<iframe id="the_frame" width="100%"style="border-radius:6px;" height="400" src="'+url+'" onload="window.open(url, \'idea!\',\'status=no,resizable=no,scrollbars=yes,personalbar=no,directories=no,location=no,toolbar=no,menubar=no,width=632,height=390,left=0,top=0\');">Enable iFrames.</iframe>'
                             +'<a href="" style="font-size:12px;position:absolute;top:0;left:0;" id="close_idea_bookmarklet">x close</a>'
                             
                             +'</div>'
                            );
                            
            $("#close_idea_bookmarklet").click(function(event){
                event.preventDefault();
                $("#idea_bookmarklet").remove();
            });
    


		})();
	}

})();

