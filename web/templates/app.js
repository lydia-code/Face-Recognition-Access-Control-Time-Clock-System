$(document).ready(function () {
  // 處理日期區間選擇功能
  $("#start-date").on("change", function () {
    var startDate = $(this).val();
    $("#end-date").attr("min", startDate);
  });

  $("#end-date").on("change", function () {
    var endDate = $(this).val();
    $("#start-date").attr("max", endDate);
  });

  // 獲取員工列表
  $.get("/get_employee_list", function (data) {
    var select = $("#employee-name");
    select.empty().append('<option value="">請選擇</option>');
    $.each(data, function (index, employee) {
      select.append(
        '<option value="' + employee.id + '">' + employee.name + "</option>"
      );
    });
  });

  // 處理打卡紀錄查詢
  $("#attendance-form").on("submit", function (e) {
    e.preventDefault();
    var formData = $(this).serialize();
    $.get("/get_attendance_records", formData, function (data) {
      var tableBody = $("#attendance-records tbody");
      tableBody.empty();
      $.each(data, function (index, record) {
        var row =
          "<tr>" +
          "<td>" +
          record.date +
          "</td>" +
          "<td>" +
          record.time +
          "</td>" +
          "<td>" +
          record.name +
          "</td>" +
          "<td>" +
          record.employee_id +
          "</td>" +
          "</tr>";
        tableBody.append(row);
      });
    });
  });
});
