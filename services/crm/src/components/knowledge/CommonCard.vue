<script setup lang="ts">
import { PropType } from "vue";
import { BusinessCard } from "@/components/knowledge";

const props = defineProps({
	card: {
		type: Object as PropType<BusinessCard>,
		required: true,
	},
});
</script>
<template>
	<div class="common-card">{{ props.card.title }}</div>
</template>
<style scoped lang="scss"></style>
