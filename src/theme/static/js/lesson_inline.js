(function ($) {
  $(document).ready(function () {
    function toggleFields(prefix) {
      var lessonTypeSelector = $("#id_" + prefix + "-lesson_type");
      var lessonType = lessonTypeSelector.val();

      // Adjust the selectors based on your field names and HTML structure
      var contentRow = $("#id_" + prefix + "-content").closest(".form-row");
      var videoRow = $("#id_" + prefix + "-video").closest(".form-row");
      var thumbnailRow = $("#id_" + prefix + "-thumbnail").closest(".form-row");
      var displayVideoRow = $("#id_" + prefix + "-display_video").closest(
        ".form-row"
      );

      if (lessonType === "VIDEO") {
        contentRow.hide();
        videoRow.show();
        thumbnailRow.show();
        displayVideoRow.show();
      } else if (lessonType === "BLOG") {
        contentRow.show();
        videoRow.hide();
        thumbnailRow.hide();
        displayVideoRow.hide();
      } else {
        contentRow.hide();
        videoRow.hide();
        thumbnailRow.hide();
        displayVideoRow.hide();
      }
    }

    function setupToggle(prefix) {
      toggleFields(prefix);
      $("#id_" + prefix + "-lesson_type").change(function () {
        toggleFields(prefix);
      });
    }

    // Initialize for existing forms
    $("div.inline-group")
      .find(".inline-related")
      .each(function () {
        var prefix = $(this)
          .find("input, select, textarea")
          .first()
          .attr("id")
          .split("-")
          .slice(0, -1)
          .join("-");
        setupToggle(prefix);
      });

    // Initialize for dynamically added forms
    $(document).on("click", ".add-row, .add-row a", function (e) {
      e.preventDefault();
      var totalFormsInput = $("#id_" + prefix + "-TOTAL_FORMS");
      var totalForms = parseInt(totalFormsInput.val());
      var newForm = $(".inline-related").last().clone(true);
      var prefix = newForm
        .find("input, select, textarea")
        .first()
        .attr("id")
        .split("-")
        .slice(0, -1)
        .join("-");
      newForm.find(":input").each(function () {
        var name = $(this)
          .attr("name")
          .replace(/-\d+-/, "-" + totalForms + "-");
        var id = "id_" + name;
        $(this).attr({ name: name, id: id }).val("");
      });
      newForm.insertBefore($(this).closest(".inline-related").next(".add-row"));
      totalFormsInput.val(totalForms + 1);
      setupToggle(prefix);
    });
  });
})(django.jQuery);
