const tabla = document.getElementById("tablaProductos");
const btnGuardar = document.getElementById("btnGuardar");

let productos = [];

// Cargar productos de la categoría
fetch(`/admin/update/productos/${idCategoria}`)
    .then(r => r.json())
    .then(data => {

        productos = data;

        data.forEach(producto => {

            const fila = document.createElement("tr");

            fila.innerHTML = `
                <td>${producto.nombre}</td>

                <td>
                    <input
                        type="number"
                        value="${producto.precio}"
                        data-id="${producto.id_producto}"
                        data-original="${producto.precio}"
                        data-nombre="${producto.nombre}"
                        class="precio-input">
                </td>
            `;

            tabla.appendChild(fila);
        });

        // Detectar cambios
        document.querySelectorAll(".precio-input").forEach(input => {

            input.addEventListener("input", () => {

                btnGuardar.disabled = false;

            });

        });

    });


// Guardar cambios
btnGuardar.addEventListener("click", () => {

    const datos = [];
    const modificados = [];

    document.querySelectorAll(".precio-input").forEach(input => {

        if (input.value != input.dataset.original) {

            datos.push({
                id_producto: input.dataset.id,
                precio: input.value
            });

            modificados.push(input.dataset.nombre);
        }

    });

    if (datos.length === 0)
        return;

    fetch("/admin/update/precios", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify(datos)

    })
        .then(r => r.json())
        .then(res => {

            const contenedor = document.getElementById("contenedorMensajes");

            const mensaje = document.createElement("div");
            mensaje.className = "mensaje-actualizacion";

            mensaje.innerHTML = `
    <strong>✓ Se actualizaron correctamente:</strong><br>
    ${modificados.join(", ")}
`;

            // Agrega el mensaje al principio
            console.log(contenedor);
            contenedor.prepend(mensaje);

            // Mostrar con animación
            requestAnimationFrame(() => {
                mensaje.classList.add("mostrar");
            });

            // Ocultarlo después de 5 segundos
            setTimeout(() => {

                mensaje.classList.remove("mostrar");

                setTimeout(() => {
                    mensaje.remove();
                }, 300);

            }, 8000);

            btnGuardar.disabled = true;

            // Actualizar el precio original para que no vuelva a detectarlo como cambiado
            document.querySelectorAll(".precio-input").forEach(input => {
                input.dataset.original = input.value;
            });

        });

});