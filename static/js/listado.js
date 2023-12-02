const URL = "http://127.0.0.1:5000/"

fetch(URL + 'reservas')
    .then(function (response) {
        if (response.ok) {
            return response.json();
    }
})
    .then(function (data) {
        let tablaReservas = document.getElementById('tablaReservas');
        for (let reserva of data) {
            let fila = document.createElement('tr');
            let fechaLlegada = new Date(reserva.fecha_llegada).toLocaleDateString();
            let fechaSalida = new Date(reserva.fecha_salida).toLocaleDateString();

            fila.innerHTML = '<td>' + reserva.codigo + '</td>' +
            '<td>' + fechaLlegada + '</td>' +
            '<td>' + fechaSalida + '</td>' +
            '<td>' + reserva.habitacion + '</td>' +
            '<td>' + reserva.apellido + '</td>' +
            '<td>' + reserva.nombre + '</td>' +
            '<td>' + reserva.dni + '</td>' +
            '<td>' + reserva.telefono + '</td>' +
            '<td>' + reserva.email + '</td>';
            tablaReservas.appendChild(fila);
    }
})
.catch(function (error) {
// Código para manejar errores
alert('Error al obtener las reservas.');
});
