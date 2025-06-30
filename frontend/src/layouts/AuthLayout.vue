<template>
  <q-layout view="lHh Lpr lFf">
    <q-page-container>
      <div class="row justify-center items-center" style="min-height: 100vh;">
        <div class="col-xs-12 col-sm-8 col-md-6 col-lg-4">
          <q-card class="card-shadow">
            <q-card-section class="text-center q-pb-none">
              <h4 class="text-h4 q-mb-md">Sistema Financeiro</h4>
            </q-card-section>

            <router-view />
          </q-card>
        </div>
      </div>
    </q-page-container>
  </q-layout>
</template>

<script>
export default {
  name: 'AuthLayout'
}
</script>

<style lang="scss" scoped>
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f5f5;
}

.auth-card {
  width: 100%;
  max-width: 400px;
  padding: 40px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 1px 5px rgba(0, 0, 0, 0.2);
}
</style> 