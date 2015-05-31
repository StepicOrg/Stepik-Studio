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
        var delete_ajax_call = function (url) {
            $.ajax({
                beforeSend: cookie_csrf_updater,
                url: url,
                type: 'DELETE',
                success: function (result) {
                    _this.props.updateComponent(_this.props.obj);
                },
                error: function (result) {
                    console.log(result);
                }
            })
        };
        delete_ajax_call(this.state.del_url);
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

var Confirm, Modal, Promise, button, confirm, div, h4, ref;

Promise = $.Deferred;

ref = React.DOM, div = ref.div, button = ref.button, h4 = ref.h4;

Modal = React.createClass({
  displayName: 'Modal',
  backdrop: function() {
    return div({
      className: 'modal-backdrop in'
    });
  },
  modal: function() {
    return div({
      className: 'modal in',
      tabIndex: -1,
      role: 'dialog',
      'aria-hidden': false,
      ref: 'modal',
      style: {
        display: 'block'
      }
    }, div({
      className: 'modal-dialog'
    }, div({
      className: 'modal-content'
    }, this.props.children)));
  },
  render: function() {
    return div(null, this.backdrop(), this.modal());
  }
});

Confirm = React.createClass({
  displayName: 'Confirm',
  getDefaultProps: function() {
    return {
      confirmLabel: 'OK',
      abortLabel: 'Cancel'
    };
  },
  abort: function() {
    return this.promise.reject();
  },
  confirm: function() {
    return this.promise.resolve();
  },
  componentDidMount: function() {
    this.promise = new Promise();
    return React.findDOMNode(this.refs.confirm).focus();
  },
  render: function() {
    return React.createElement(Modal, null, div({
      className: 'modal-header'
    }, h4({
      className: 'modal-title'
    }, this.props.message)), this.props.description ? div({
      className: 'modal-body'
    }, this.props.description) : void 0, div({
      className: 'modal-footer'
    }, div({
      className: 'text-right'
    }, button({
      role: 'abort',
      type: 'button',
      className: 'btn btn-default',
      onClick: this.abort
    }, this.props.abortLabel), ' ', button({
      role: 'confirm',
      type: 'button',
      className: 'btn btn-primary',
      ref: 'confirm',
      onClick: this.confirm
    }, this.props.confirmLabel))));
  }
});

confirm = function(message, options) {
  var cleanup, component, props, wrapper;
  if (options == null) {
    options = {};
  }
  props = $.extend({
    message: message
  }, options);
  wrapper = document.body.appendChild(document.createElement('div'));
  component = React.render(React.createElement(Confirm, props), wrapper);
  cleanup = function() {
    React.unmountComponentAtNode(wrapper);
    return setTimeout(function() {
      return wrapper.remove();
    });
  };
  return component.promise.always(cleanup).promise();
};

$(function() {
  return $('.removable').click(function() {
    return confirm('Are you sure?', {
      description: 'Would you like to remove this item from the list?',
      confirmLabel: 'Yes',
      abortLabel: 'No'
    }).then((function(_this) {
      return function() {
        return $(_this).parent().remove();
      };
    })(this));
  });
});


var SubStepComponent = React.render(
  <SubStepMAIN data-info="data" step_id={connect_elem.attributes.data_id.value} data="somedata"/>,
  connect_elem
);