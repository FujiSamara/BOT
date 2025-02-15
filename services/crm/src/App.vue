<script setup lang="ts">
import LoadingPage from "@/pages/LoadingPage.vue";
import { useNetworkStore } from "./store/network";

const networkStore = useNetworkStore();
</script>
<template>
	<LoadingPage v-if="networkStore.authing"></LoadingPage>
	<router-view v-show="!networkStore.authing"></router-view>
</template>
<style></style>
