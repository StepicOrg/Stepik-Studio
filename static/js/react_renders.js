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
        var _this = this;
        var delete_ajax_call = function () {
            $.ajax({
                beforeSend: cookie_csrf_updater,
                url: _this.state.del_url,
                type: 'DELETE',
                success: function (result) {
                    _this.props.updateComponent(_this.props.obj);
                },
                error: function (result) {
                    console.log(result);
                }
            })
        };
        delete_ajax_call();
    },

    openDialog: function(e){
        var _this = this;
        e.preventDefault();
        var $dialog = $('<div>').dialog({
            title: 'Are you sure?',
            width: 400,
            close: function(e){
              //React.unmountComponentAtNode(this);
              $( this ).remove();
            }
        });
        var deleteRecord = function (e) {
            _this.handleClick();
            $dialog.dialog('close');
        };

        var cancelEvent = function(e){
            e.preventDefault();
            $dialog.dialog('close');
        };
        React.render(<DialogContent closeDialog={cancelEvent} deleteRecord={deleteRecord}/>, $dialog[0])
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
                    <span onClick= {this.openDialog} obj={this} data="NOOO">Delete</span>
                </span>
            </div>
        );
    }
});


var SubStepBox = React.createClass({

    loadData: function(){
        return $.get('/api/step/'+this.props.step_id+'/');
    },

    updateComponent: function(obj){
        obj.loadData().then(function(data){
          this.setState({
              data: data,
              substep_list: data.substep_list
          });
      }.bind(obj));
    },


    getInitialState: function(){
        return {
            data: this.props.data,
            substep_list: this.props.substep_list
        };
    },

    componentWillReceiveProps: function(nextProps) {
        this.setState({
              data: nextProps,
              substep_list: nextProps.substep_list
          });
    },

    render: function() {
        var Th = this;
        return (
          <div className="substepBox">
              I am a box.
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

    loadData: function(){
        return $.get('/api/step/'+this.props.step_id+'/');
    },


    componentDidMount: function(){
        var _this = this;
      this.loadData().then(function(data){
          this.setState({
              data: data,
              substep_list: data.substep_list
          });
      }.bind(this));
    },

    componentWillReceiveProps: function(nextProps) {
        this.setState({
              data: nextProps,
              substep_list: nextProps.substep_list
          });
    },

    getInitialState: function(){
        return {
            data: 'No Data',
            substep_list: [{name:'No Step', id:'0'}]
        };
    },

    render: function () {
        return (
            <SubStepBox data-info="data" step_id={this.props.step_id} data={this.state.data} substep_list={this.state.substep_list}/>
        )
    }
});

var DialogContent = React.createClass({
    render: function(){
      return(
      <div>
            <button onClick = {this.props.deleteRecord}>Yes</button><span>________</span>
            <button onClick = {this.props.closeDialog}>Cancel</button>
      </div>
      )
    }
  });


var SubStepComponent = React.render(
  <SubStepMAIN data-info="data" step_id={connect_elem.attributes.data_id.value} data="somedata"/>,
  connect_elem
);