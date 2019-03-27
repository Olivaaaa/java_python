$(function () {
    $('#selectDrug').click(function (e) {
        e.preventDefault();
        var url = '/executescript';
        var name = $('#name').val();
        var min = $('#min').val();
        var max = $('#max').val();
        var OR = $('#OR').val();

        var data = {
            'name':name,
            'min':min,
            'max':max,
            'OR':OR
        }
        console.log(data);
        $.ajax({
            url:url,
            type:'post',
            data:data,
            success:function () {
                if (name.trim() == 'ACEI'.trim()){
                    alert("成功");
                }
            },
            error:function () {
                
            }
        })
    })
})