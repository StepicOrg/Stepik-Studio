/** @jsx React.DOM */

var SubStepLinks = React.createClass({



    render: function(){
        return (
            <span>
                <img class src="/static/icons/video-camera.svg"></img>
            </span>
        )
    }
});


var SubStep = React.createClass({

    getInitialState: function(){
        return {
            data: 'No Step',
            del_url: "/api/substep/"+ this.props.substep.id + "/",
            update: '2'
        };
    },

    handleClick: function(event) {
        var delete_ajax_call = function (url) {
            $.ajax({
                beforeSend: cookie_csrf_updater,
                url: url,
                type: 'DELETE',
                success: function (result) {
                },
                error: function (result) {
                    console.log(result);
                }
            })
        };
        delete_ajax_call(this.state.del_url);
        this.props.updateComponent(this.props.obj);
    },

    render: function(){

        var prof_file = '/showcontent/'+ this.props.substep.id + "/";
        var scr_file = '/showscreencontent/'+ this.props.substep.id + "/";

        return (
            <div className="substep-list" valueLink={this.props.value}>
                <span className="substep-name">
                    {this.props.substep.name}
                </span>
                <span className="subStepLinks">
                    | <a target="_blank" href={prof_file}><img src="/static/icons/video-camera.svg"></img></a> |
                     <a target="_blank" href={scr_file}><img onClick={this.downloadVideoScreen} src="/static/icons/display.svg"></img></a> |
                </span>
                <span className="delete_button right">
                    <span onClick={this.handleClick} className='delete_button'>Delete</span>
                </span>
            </div>
        );
    }
});


var SubStepBox = React.createClass({

    loadData: function(){
        return $.get('/api/step/'+this.props.step_id+'/');
    },

    componentDidMount: function(){
      this.loadData().then(function(data){
          //console.log(data);
          this.setState({
              data: data,
              substep_list: data.substep_list
          });
      }.bind(this));
        console.log(this.state);
    },

    getInitialState: function(){
        return {
            data: 'No Step',
            substep_list: [{name:'No Step', id:'0'}]
        };
    },


    updateComponent: function(obj){
        console.log(obj);
        obj.loadData().then(function(data){
          //console.log(data);
          this.setState({
              data: data,
              substep_list: data.substep_list
          });
      }.bind(obj));

    },

    render: function() {
        var Th = this;
        return (
          <div className="substepBox">
              I am a CommentBox.
              StateValue: {this.state.value}
              ThisProps: {this.props}
              <div updateComponent={this.updateComponent}> UpdateComponent </div>
              {this.state.substep_list.map(function(substep){
                    return <SubStep substep={substep} key={substep.id} updateComponent={Th.updateComponent} obj={Th} data={Th.state.substep_list} />
              })}
          </div>
        );
    }
});

connect_elem = document.getElementById('SubstepList');


var SubStepMAIN = React.createClass({




    render: function () {
        return (
            <SubStepBox data-info="data" step_id={this.props.step_id}/>
        )
    }
});

var SubStepComponent = React.render(
  <SubStepMAIN data-info="data" step_id={connect_elem.attributes.data_id.value}/>,
  connect_elem
);