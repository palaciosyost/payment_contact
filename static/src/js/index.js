/** @odoo-module **/

function initReniecWatcher() {
  const $partner_name = document.getElementById("o_name");
  const $input_vat = document.getElementById("o_vat");
  const $type_ident = document.querySelector("select[name='l10n_latam_identification_type_id']");
  const $company_name = document.getElementById("o_company_name");
  const $company_div = document.getElementById("company_name_div");
  const $direccion = document.getElementById("o_street");

  if (
      !$partner_name || !$input_vat || !$company_name ||
      !$direccion || !$company_div || !$type_ident
  ) {
      return setTimeout(initReniecWatcher, 300);
  }

  $company_div.style.display = "none";


  $input_vat.addEventListener("keyup", (e) => {
      const numero = e.target.value.trim();
      console.log(numero)
      if (numero.length === 0) {
          $partner_name.value = "";
          $company_name.value = "";
          $company_div.style.display = "none";
          return;
      }

      if (numero.length === 8 || numero.length === 11) {
          fetch("/api/consulta_documento/" + numero)
              .then((res) => res.json())
              .then((data) => {
                  if (data.error) return;
                  console.log(data)
                  if (data.nombreCompleto) {
                      $partner_name.value = data.nombreCompleto;
                      $type_ident.value = "5"; // DNI
                      $company_div.style.display = "none";
                  }

                  if (data.razonSocial) {
                      $company_name.value = data.razonSocial;
                      $type_ident.value = "4"; // RUC
                      $direccion.value = data.direccion;
                      $company_div.style.display = "block";
                  }
              })
              .catch((err) => console.error("❌ Error al consultar documento:", err));
      }
  });

  $type_ident.addEventListener("change", () => {
      if ($type_ident.value === "6") {
          $company_div.style.display = "block";
      } else {
          $company_div.style.display = "none";
          $company_name.value = "";
      }
  });
}

// ✅ Ejecutar solo si estamos en /shop/address
if (window.location.pathname.includes("/shop/address")) {
  setTimeout(initReniecWatcher, 500);
}
