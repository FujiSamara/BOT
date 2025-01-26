<script setup lang="ts">
import Checkbox from "@/components/UI/Checkbox.vue";
import SearchInput from "@/components/SearchInput.vue";
import { BaseEntity } from ".";
import { PropType, ref } from "vue";
import { computed } from "@vue/reactivity";
import * as animations from "@/components/entity/animations";

const props = defineProps({
	entity: {
		type: Object as PropType<BaseEntity<any>>,
		required: true,
	},
});
const entity = props.entity;

const active = ref(false);
const entities = computed(() => {
	if (!active.value) {
		return [];
	}
	return entity.entitiesList.value;
});
const error = computed(() => {
	if (
		entity.entitiesList.value.length - entity.selectedEntities.value.length ===
			0 &&
		entity.formattedField.value.length !== 0 &&
		!entity.loading.value
	) {
		return "";
	}
	return undefined;
});
</script>

<template>
	<div
		class="entity-search"
		@focusin="active = true"
		@focusout="active = false"
	>
		<SearchInput
			class="search-input"
			:value="entity.formattedField.value"
			@submit="(val: string) => (entity.formattedField.value = val)"
			:error="error"
			:placeholder="entity.placeholder"
		></SearchInput>
		<TransitionGroup
			:css="false"
			tag="ul"
			class="entity-list"
			@before-enter="animations.onBeforeEnter"
			@enter="animations.onEnter"
			@leave="animations.onLeave"
			@pointerdown.prevent
		>
			<li
				class="entity-wrapper"
				:key="entityRow.value + (entityRow.checked ? 'c' : 'unc')"
				v-for="(entityRow, index) in entities"
				:data-index="index"
			>
				<div class="entity">
					{{ entityRow.value }}
				</div>
				<Checkbox :checked="entityRow.checked" @click="entity.select(index)">
				</Checkbox>
			</li>
		</TransitionGroup>
	</div>
</template>

<style scoped lang="scss">
.entity-search {
	display: flex;
	flex-direction: column;
	gap: 16px;

	.search-input {
		width: 248px;
	}

	.entity-list {
		display: flex;
		flex-direction: column;
		gap: 10px;

		width: 248px;
		padding: 0;

		.entity-wrapper {
			@include field;
			width: inherit;
			justify-content: space-between;

			.entity {
				overflow-x: hidden;
			}
		}

		&:empty {
			margin-top: calc(-16px);
		}
	}
}
</style>
