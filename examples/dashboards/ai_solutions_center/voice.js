require([
    "jquery",
    "splunkjs/mvc",
    "splunkjs/mvc/simplexml/ready!"
], function($, mvc) {
    console.log("Loaded voice.js");
    $(document).on("click", '#speakButton', function() {
        var inputTxt = $('#inputTxt').val();
        var inputLang = $('#inputLang').val();
        var synth = window.speechSynthesis;
        if (synth.speaking) {
            synth.cancel();
        }
        var msg = new SpeechSynthesisUtterance(inputTxt);
		msg.lang = inputLang;
        synth.speak(msg);
    });
    $(document).on("click", '#stopButton', function() {
        var synth = window.speechSynthesis;
        if (synth.speaking) {
            synth.cancel();
        }
    });	
});
