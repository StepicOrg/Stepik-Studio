this["JST"] = this["JST"] || {};

this["JST"]["static/extra/hb_templates/test.handlebars"] = Handlebars.template({"compiler":[6,">= 2.0.0-beta.1"],"main":function(depth0,helpers,partials,data) {
    var helper;

  return "<div class=\"input-step-name-field\">\n           <form id=\"rename-step-form\" action=\"javascript:void(0);\">\n           <input id=\"input-field-name\" type=\"text\"> "
    + this.escapeExpression(((helper = (helper = helpers.name || (depth0 != null ? depth0.name : depth0)) != null ? helper : helpers.helperMissing),(typeof helper === "function" ? helper.call(depth0,{"name":"name","hash":{},"data":data}) : helper)))
    + "\n               <input id=\"cancel-rename\" type=\"submit\" value=\"Cancel\">\n           </form>\n</div>";
},"useData":true});