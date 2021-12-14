var id

var base_url="http://5dae-34-86-132-116.ngrok.io"

$(function() {
  // Send a message to content.js to fetch all the top domains
  chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    var activeTab = tabs[0];
    chrome.tabs.sendMessage(activeTab.id, {"message": "fetch_top_domains"});
  });

  // Add a listener to handle the response from content.js
  chrome.runtime.onMessage.addListener(
    function(request, sender, sendResponse) {
      if( request.message === "all_urls_fetched" ) {
        console.log(request.data)
        for ( var key in request.data ) {
          if(request.data.hasOwnProperty(key)) {
            $('#tabs_table tr:last').after('<tr><td>' + key + '</td>' + '<td>' + request.data[key] +'</td></tr>');
          }
        }
        id=request.data['title'].split('v=')[1]
        console.log(id)
      }
    }
  );
});

var myFunctionReference = function() {
  let xhr = new XMLHttpRequest();
  
  console.log(id)
  var url=base_url.concat("/summarize/?id=").concat(id)
  var choice= document.getElementById('sum_choice').value
  var percent=document.getElementById('percent').value
  url=url.concat("&percent=").concat(percent).concat("&choice=").concat(choice)
  console.log(url)
  xhr.open("GET",url)
  xhr.send()
  xhr.onload=()=>{
    console.log(xhr)
    if(xhr.status===200) {
      console.log(JSON.parse(xhr.response))
      apiResponse=JSON.parse(xhr.response)
      document.getElementById('summary').innerHTML=apiResponse['response']['processed_summary']
      console.log(apiResponse['response']['processed_summary'])
    }
    else if(xhr.status===400) {
      apiResponse=JSON.parse(xhr.response)
      document.getElementById('summary').innerHTML=apiResponse['message']
      console.log(apiResponse['response']['processed_summary'])
    }
    else{
      document.getElementById('summary').innerHTML="Error Occured"
    }
  }
};

var analyisFunction = function() {
  let xhr = new XMLHttpRequest();
  var analysis_url=base_url.concat("/analysis/?id=").concat(id)
  xhr.open("GET",analysis_url)
  xhr.send()
  xhr.onload=()=>{
    console.log(xhr)
    if(xhr.status===200) {
      console.log(JSON.parse(xhr.response))
      apiResponse=JSON.parse(xhr.response)
      document.getElementById('positive').innerHTML=apiResponse['response']['positive']
      document.getElementById('negative').innerHTML=apiResponse['response']['negative']
    }
    else{
      console.log("error")
    }
  }
};

// if (document.getElementById('getSummary')!=null){
//   document.getElementById('getSummary').addEventListener('click', myFunctionReference , false);
// }

document.addEventListener('DOMContentLoaded', function() {
  document.getElementById('getSummary').addEventListener('click', myFunctionReference , false);
});

document.addEventListener('DOMContentLoaded', function() {
  document.getElementById('getAnalysis').addEventListener('click', analyisFunction , false);
});

